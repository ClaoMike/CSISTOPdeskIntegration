import requests
from ConfigurationManager import ConfigurationManager
from TimestampGenerator import TimestampGenerator

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
            self.__configurationManager = ConfigurationManager()

            timestampGenerator = TimestampGenerator()
            self.__timestamp = timestampGenerator.get_timestamp(minutes=self.__configurationManager.minutes)

    def get_token(self):
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.__configurationManager.client_id,
            "client_secret": self.__configurationManager.client_secret,
            "scope": "https://api.csis.com/ticket:read https://api.csis.com/ticket:write"
        }

        response = requests.post(self.__configurationManager.authentication_url, data=payload)

        if response.status_code == 200:
            token = response.json().get("access_token")
            self.__configurationManager.client_token = token
        else:
            print(f"Error {response.status_code}: {response.text}")

    def get_tickets_to_be_created(self):
        """Fetch tickets created after a timestamp, that are not closed."""
        offset = 0
        limit = 2
        tickets_ids = []
        tickets = []

        while True:
            response = self.__get_tickets_with_offset(offset, limit)
            payload = response["payload"]

            for ticket in payload["page"]:
                tickets_ids.append(ticket["id"])

            if payload["has_next"] is False:
                break

            offset += limit

        # only save tickets that do not have the TOPdesk id
        for external_id in tickets_ids:
            ticket_details = self.__get_ticket(external_id)
            if ticket_details["payload"]["customer_reference"] == "" or ticket_details["payload"]["customer_reference"] is None:
                tickets.append(ticket_details)

        return tickets

    def __get_tickets_with_offset(self, offset, limit):
        """Fetch tickets created after a timestamp, that are not closed."""
        headers = {
            "Authorization": f"Bearer {self.__configurationManager.client_token}",
            "Content-Type": "application/json"
        }

        params = {
            "created_after": self.__timestamp,
            "status": ["new", "pending-customer", "pending-csis", "confirmed"],  # Ensure 'closed' is excluded
            "limit": limit,
            "offset": offset
        }

        url = f"{self.__configurationManager.base_url}/ticket/"
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None

    def __get_ticket(self, external_id):
        """Fetch ticket details by external_id."""
        headers = {
            "Authorization": f"Bearer {self.__configurationManager.client_token}",
            "Content-Type": "application/json"
        }

        url = f"{self.__configurationManager.base_url}/ticket/{external_id}"  # Construct full API URL
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()  # Return ticket details as JSON
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None  # Return None if API request fails