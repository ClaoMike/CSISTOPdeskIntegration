import requests
from ConfigurationManager import ConfigurationManager
from HttpResponseEvaluator import HttpResponseEvaluator
from src.utils.TimestampGenerator import TimestampGenerator
from HttpResponseEvaluator import RequestType
from datetime import datetime

class CsisAPI:
    _instance = None  # Singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CsisAPI, cls).__new__(cls)
            cls._instance.__initialize()
        return cls._instance

    def __initialize(self):
        if not hasattr(self, "_initialized"):
            self._initialized = True

            # Generate timestamp for filtering tickets
            timestamp_generator = TimestampGenerator()

            self.__headers = {
                "Content-Type": "application/json"
            }

    @staticmethod
    def get_token():
        """
           Fetches and stores the CSIS authentication token.
        """
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
        print("Getting tickets to_be_created")

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
            ticket["comments"] = self.__get_comments(ticket["id"])

        print(f"All tickets that must be created in TOPdesk: {tickets}")


        return tickets

    def __get_filtered_tickets(self, updated_after, status):
        """
        Fetches filtered tickets, by status and update after time.
        """
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
        """
        Fetches ticket details by external_id.
        """

        url = f"{ConfigurationManager().csis_base_url}/1.1/ticket/{external_id}"
        HttpResponseEvaluator.announce_request(url, RequestType.GET)
        response = requests.get(url=url, headers=self.__headers)
        HttpResponseEvaluator.evaluate(response)

        return response.json()["payload"]

    def __get_comments(self, ticket_id):
        """
            Fetches comments associated with a specific ticket.
        """
        url = f"{ConfigurationManager().csis_base_url}/1.0/ticket/{ticket_id}/comment"
        HttpResponseEvaluator.announce_request(url, RequestType.GET)
        response = requests.get(url=url, headers=self.__headers)
        HttpResponseEvaluator.evaluate(response)

        return response.json()["payload"]

    # def __attach_comments(self, tickets, recent=True):
    #     """
    #             Attaches recent comments to each ticket.
    #
    #             Args:
    #                 tickets (list): List of tickets.
    #
    #             Returns:
    #                 list: List of tickets with attached recent comments.
    #             """
    #
    #     if recent:
    #         last_update = datetime.fromisoformat(
    #             self.__configurationManager.last_updates_timestamp.replace("Z", "+00:00")
    #         )
    #
    #     for ticket in tickets:
    #         # get all comments in ticket
    #         all_comments = self.__get_comments(ticket["payload"]["id"])
    #
    #         # save only those that are recent
    #         recent_comments = []
    #         for comment in all_comments:
    #             if recent:
    #                 comment_created = datetime.fromisoformat(comment["created"])
    #             comment_text = comment['text']
    #
    #             if recent:
    #                 print(f"Last Update Timestamp: {last_update}")
    #             print(f"Comment timestamp: {comment_created}")
    #
    #             if not comment_text.startswith("[TOPdesk]"):
    #                 if recent:  # if recent we filter them based on date, otherwise not
    #                     if last_update < comment_created:
    #                         recent_comments.append(comment)
    #                 else:
    #                     recent_comments.append(comment)
    #
    #         ticket["comments"] = recent_comments
    #
    #     return tickets

    # def __get_updated_tickets_with_offset(self, offset, limit):
    #     """
    #     Fetches tickets that were updated after a timestamp.
    #
    #     Args:
    #         offset (int): Pagination offset for fetching tickets.
    #         limit (int): Number of tickets to fetch per request.
    #
    #     Returns:
    #         dict: JSON response containing ticket data.
    #
    #     Raises:
    #         SystemExit: If the API request fails.
    #     """
    #     params = {
    #         "updated_after": self.__configurationManager.last_updates_timestamp,
    #         "status": ["new", "pending-customer", "pending-csis", "confirmed", "closed"],
    #         "limit": limit,
    #         "offset": offset
    #     }
    #
    #     return self.__make_request(request_type=RequestType.GET, params=params)

    # def update_tickets(self, tickets):
    #     """
    #             Updates tickets with new customer references.
    #
    #             Args:
    #                 tickets (list): List of tickets to update.
    #             """
    #     for ticket in tickets:
    #         payload = {
    #             "customer_reference": ticket["number"],
    #         }
    #
    #         self.__make_request(
    #             request_type=RequestType.PATCH,
    #             payload=payload,
    #             endpoint=f"/{ticket['externalNumber']}"
    #         )

    # def get_updated_tickets(self):
    #     """
    #     Retrieves updated tickets after a timestamp and attaches recent comments.
    #
    #     Returns:
    #         list: A list of updated tickets with comments.
    #     """
    #     tickets = self.__get_filtered_tickets(self.__get_updated_tickets_with_offset,
    #                                           should_have_customer_reference=True)
    #     tickets = self.__attach_comments(tickets)
    #
    #     return tickets