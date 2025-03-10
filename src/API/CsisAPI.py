import requests
from src.config.ConfigurationManager import ConfigurationManager
from src.utils.HTTPRequestResponseEvaluator import HTTPRequestResponseEvaluator
from src.utils.Logger import Logger
from src.utils.TimestampGenerator import TimestampGenerator

class CsisAPI:
    _instance = None  # Class variable to store the single instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CsisAPI, cls).__new__(cls)
            cls._instance.__initialize()  # Call internal initialization
        return cls._instance

    def __initialize(self):
        """This method initializes attributes only once."""
        if not hasattr(self, "_initialized"):  # Ensure it's only initialized once
            self._initialized = True
            self.__logger = Logger()
            self.__responseEvaluator = HTTPRequestResponseEvaluator()

            self.__configurationManager = ConfigurationManager()

            timestampGenerator = TimestampGenerator()
            self.__timestamp = timestampGenerator.get_timestamp(minutes=self.__configurationManager.minutes)
            self.__logger.info(f"Current timestamp: {self.__timestamp}")

    def get_token(self):
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.__configurationManager.csis_client_id,
            "client_secret": self.__configurationManager.csis_client_secret,
            "scope": "https://api.csis.com/ticket:read https://api.csis.com/ticket:write"
        }

        response = requests.post(self.__configurationManager.csis_authentication_url, data=payload)
        self.__responseEvaluator.evaluate(response)

        token = response.json().get("access_token")
        self.__configurationManager.csis_client_token = token

    def get_tickets_to_be_created(self):
        """Fetch tickets created after a timestamp, that are not closed."""
        return self.__get_filtered_tickets(self.__get_tickets_with_offset, "created_after", should_have_customer_reference=False)

    def get_updated_tickets(self):
        """Fetch tickets updated after a timestamp."""
        tickets = self.__get_filtered_tickets(self.__get_updated_tickets_with_offset, "updated_after", should_have_customer_reference=True)
        tickets = self.__attach_comments(tickets)

        return tickets

    def __get_tickets_with_offset(self, offset, limit):
        """Fetch tickets created after a timestamp, that are not closed."""
        return self.__get_tickets(offset, limit, "created_after",
                                  ["new", "pending-customer", "pending-csis", "confirmed"])

    def __get_updated_tickets_with_offset(self, offset, limit):
        """Fetch tickets updated after a timestamp."""
        return self.__get_tickets(offset, limit, "updated_after",
                                  ["new", "pending-customer", "pending-csis", "confirmed", "closed"])

    def __get_tickets(self, offset, limit, timestamp_key, status_list):
        """Generic method to fetch tickets based on creation or update timestamp."""
        headers = {
            "Authorization": f"Bearer {self.__configurationManager.csis_client_token}",
            "Content-Type": "application/json"
        }

        params = {
            timestamp_key: self.__timestamp,
            "status": status_list,
            "limit": limit,
            "offset": offset
        }

        url = f"{self.__configurationManager.csis_base_url}/ticket/"

        response = requests.get(url, headers=headers, params=params)
        self.__responseEvaluator.evaluate(response)

        return response.json()

    def __get_filtered_tickets(self, fetch_function, timestamp_key, should_have_customer_reference):
        """Fetch and filter tickets based on the given fetch function."""
        offset = 0
        limit = 2
        tickets_ids = []
        tickets = []

        while True:
            response = fetch_function(offset, limit)
            if response is None:
                break  # Exit on error

            payload = response["payload"]

            for ticket in payload["page"]:
                tickets_ids.append(ticket["id"])

            if not payload.get("has_next", False):
                break

            offset += limit

        # Only save tickets that do not have a TOPdesk ID
        for external_id in tickets_ids:
            ticket_details = self.__get_ticket(external_id)
            if should_have_customer_reference:
                if ticket_details["payload"].get("customer_reference") not in ("", None):
                    tickets.append(ticket_details)
            else:
                if ticket_details["payload"].get("customer_reference") in ("", None):
                    tickets.append(ticket_details)

        return tickets

    def __get_tickets_with_offset(self, offset, limit):
        """Fetch tickets created after a timestamp, that are not closed."""
        headers = {
            "Authorization": f"Bearer {self.__configurationManager.csis_client_token}",
            "Content-Type": "application/json"
        }

        params = {
            "created_after": self.__timestamp,
            "status": ["new", "pending-customer", "pending-csis", "confirmed"],  # Ensure 'closed' is excluded
            "limit": limit,
            "offset": offset
        }

        url = f"{self.__configurationManager.csis_base_url}/ticket/"

        response = requests.get(url, headers=headers, params=params)
        self.__responseEvaluator.evaluate(response)

        return response.json()

    def __get_ticket(self, external_id):
        """Fetch ticket details by external_id."""
        headers = {
            "Authorization": f"Bearer {self.__configurationManager.csis_client_token}",
            "Content-Type": "application/json"
        }

        url = f"{self.__configurationManager.csis_base_url}/ticket/{external_id}"  # Construct full API URL

        response = requests.get(url, headers=headers)
        self.__responseEvaluator.evaluate(response)

        return response.json()  # Return ticket details as JSON

    def update_tickets(self, tickets):
        for ticket in tickets:
            self.__update_ticket(ticket)

    def __update_ticket(self, ticket):
        print(f"Updating: {ticket}")
        url = f"{self.__configurationManager.csis_base_url}/ticket/{ticket["externalNumber"]}"  # Construct full API URL

        payload = {
            "customer_reference": ticket["number"],
        }

        headers = {
            "Authorization": f"Bearer {self.__configurationManager.csis_client_token}",
            "Content-Type": "application/json"
        }

        response = requests.patch(
            url,
            headers=headers,
            json=payload
        )
        self.__responseEvaluator.evaluate(response)

    def __attach_comments(self, tickets):
        for ticket in tickets:
            # get all comments in ticket
            all_comments = self.__get_comments(ticket["payload"]["id"])

            # save only those that are recent
            recent_comments = []
            for i in range(len(all_comments)):
                timestampGenerator = TimestampGenerator()
                time_difference = timestampGenerator.get_time_difference_between(self.__timestamp, all_comments[i]["created"]) # in minutes
                if time_difference < self.__configurationManager.minutes:
                    recent_comments.append(all_comments[i])

            ticket["comments"] = recent_comments

        return tickets

    def __get_comments(self, ticket_id):
        url = f"{self.__configurationManager.csis_base_url}/ticket/{ticket_id}/comment"

        headers = {
            "Authorization": f"Bearer {self.__configurationManager.csis_client_token}",
            "Content-Type": "application/json"
        }

        response = requests.get(
            url,
            headers=headers
        )
        self.__responseEvaluator.evaluate(response)

        return response.json()["payload"]

