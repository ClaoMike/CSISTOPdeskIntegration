import requests
from ConfigurationManager import ConfigurationManager
from HttpResponseEvaluator import RequestType, HttpResponseEvaluator
from TimestampUtils import TimestampUtils
from Singleton import Singleton

class CsisAPI(Singleton):
    def _init_singleton(self):
        self.__headers = { "Content-Type": "application/json" }

    @staticmethod
    def get_token():
        """Fetches and stores the CSIS authentication token."""
        cm = ConfigurationManager()
        payload = {
            "grant_type": "client_credentials",
            "client_id": cm.csis_client_id,
            "client_secret": cm.csis_client_secret,
            "scope": "https://api.csis.com/ticket:read https://api.csis.com/ticket:write"
        }

        HttpResponseEvaluator.announce_request(cm.csis_authentication_url, RequestType.GET)
        response = requests.post(cm.csis_authentication_url, data=payload)
        HttpResponseEvaluator.evaluate(response, hide_response=True)

        return response.json().get("access_token")

    def set_authorization_token(self):
        auth_token = ConfigurationManager().csis_client_token
        print(f"Setting authorization token: {ConfigurationManager.hide_data(auth_token)}")

        self.__headers["Authorization"] = f"Bearer {auth_token}"

    def get_tickets_to_be_created(self):
        """
        Retrieves tickets that:
        - have been created after the last saved timestamp;
        - have their status set to either Pending Customer or Confirmed;
        - do not have a TOPdesk ID;
        - along with their comments;
        """
        print("Getting tickets to be created")

        # get filtered tickets
        tickets = self.__get_filtered_tickets(
            ConfigurationManager().last_new_tickets_timestamp,
            ["pending-customer", "confirmed"]
        )
        print(f"All tickets: {tickets}")

        # get their details
        tickets = self.__get_details_for_tickets(tickets)
        print(f"Detailed tickets: {tickets}")

        # filter out those that have been created in TOPdesk already
        _, tickets = self.__filter_tickets_by_customer_reference(tickets)
        print(f"Tickets without customer referene: {tickets}")

        # get comments
        for ticket in tickets:
            comments = self.__get_comments(ticket["id"])
            comments.reverse() # reverse them to display them in order of appearance in topdesk
            if comments is not None and len(comments) > 0:
                ticket["comments"] = comments

        print(f"All tickets that must be created in TOPdesk: {tickets}")

        return tickets

    def get_tickets_to_be_updated(self):
        """
        Retrieves tickets that:
        - have been updated after the last saved timestamp;
        - have their status set to either New, Pending Customer, Pending Csis, Confirmed, Closed
        - have a TOPdesk ID;
        - along with their comments;
        """
        print("Getting tickets to be updated")

        # get filtered tickets
        tickets = self.__get_filtered_tickets(
            ConfigurationManager().last_updates_timestamp,
            # "2025-12-15T09:00:00Z", # use this for testing purposes
            ["new", "pending-customer", "pending-csis", "confirmed", "closed"]
        )
        print(f"All tickets: {tickets}")

        # get their details
        tickets = self.__get_details_for_tickets(tickets)
        print(f"Detailed tickets: {tickets}")

        # filter out those that have been created in TOPdesk already
        tickets, _ = self.__filter_tickets_by_customer_reference(tickets)
        print(f"Tickets with customer reference: {tickets}")

        # get comments
        for ticket in tickets:
            comments = self.__get_comments(ticket["id"])
            comments.reverse() # reverse them to display them in order of appearance in topdesk

            comments = self.__filter_comments_by_date(comments)
            comments = self.__filter_comments_by_creator(comments)

            if comments is not None and len(comments) > 0:
                ticket["comments"] = comments

        print(f"All tickets that must be updated in TOPdesk: {tickets}")

        return tickets

    def update_tickets_with_customer_reference(self, tickets):
        """Updates tickets with new customer references."""
        for ticket in tickets:
            payload = {
                "customer_reference": ticket["topdesk_id"],
            }

            self.__update_ticket( ticket["csis_id"], payload)

    def __filter_comments_by_date(self, comments):
        last_updated_timestamp = TimestampUtils.convert_UTC_z_to_ISO8601(ConfigurationManager().last_updates_timestamp)

        recent_comments = []
        for comment in comments:
            comment_date = TimestampUtils.convert_UTC_z_to_ISO8601(
                TimestampUtils.convert_csis_time_to_UTC_z(comment["created"])
            )

            if comment_date >= last_updated_timestamp:
                recent_comments.append(comment)

        return recent_comments

    def __filter_comments_by_creator(self, comments):
        recent_comments = []
        for comment in comments:
            if not comment["text"].startswith("[TOPdesk]"):
                recent_comments.append(comment)

        return recent_comments

    def __update_ticket(self, ticket_id, payload):
        """Updates ticket."""
        url = f"{ConfigurationManager().csis_base_url}/1.0/ticket/{ticket_id}"

        HttpResponseEvaluator.announce_request(url, RequestType.PATCH, json=payload)
        response = requests.patch(url=url, headers=self.__headers, json=payload)
        HttpResponseEvaluator.evaluate(response)

    def __get_filtered_tickets(self, updated_after, status):
        """Fetches filtered tickets, by status and update after time."""
        offset = 0
        limit = 10
        tickets = []

        url = f"{ConfigurationManager().csis_base_url}/1.1/ticket/"
        params = {
            "updated_after": updated_after,
            "status": status,
        }

        while True:
            params["offset"] = offset
            params["limit"] = limit

            HttpResponseEvaluator.announce_request(url, RequestType.GET)
            response = requests.get(url=url, headers=self.__headers, params=params)
            HttpResponseEvaluator.evaluate(response)

            payload = response.json()["payload"]

            for ticket in payload["page"]:
                tickets.append(ticket)

            if not payload.get("has_next", False):
                break

            offset += limit

        return tickets

    def __get_details_for_tickets(self, tickets):
        detailed_tickets = []
        for ticket in tickets:
            detailed_tickets.append(self.__get_ticket(ticket["id"]))

        return detailed_tickets

    def __filter_tickets_by_customer_reference(self, tickets):
        tickets_with_customer_reference     = []
        tickets_without_customer_reference  = []

        for ticket in tickets:
            if ticket.get("customer_reference") not in ("", None):
                tickets_with_customer_reference.append(ticket)
            else:
                tickets_without_customer_reference.append(ticket)

        return tickets_with_customer_reference, tickets_without_customer_reference

    def __get_ticket(self, external_id):
        """Fetches ticket details by external_id."""
        url = f"{ConfigurationManager().csis_base_url}/1.1/ticket/{external_id}"
        HttpResponseEvaluator.announce_request(url, RequestType.GET)
        response = requests.get(url=url, headers=self.__headers)
        HttpResponseEvaluator.evaluate(response)

        return response.json()["payload"]

    def __get_comments(self, ticket_id):
        """Fetches comments associated with a specific ticket."""
        url = f"{ConfigurationManager().csis_base_url}/1.0/ticket/{ticket_id}/comment"
        HttpResponseEvaluator.announce_request(url, RequestType.GET)
        response = requests.get(url=url, headers=self.__headers)
        HttpResponseEvaluator.evaluate(response)

        return response.json()["payload"]