import requests
from ConfigurationManager import ConfigurationManager

class TOPdeskAPI:
    _instance = None  # Singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TOPdeskAPI, cls).__new__(cls)
            cls._instance.__initialize()
        return cls._instance

    def __initialize(self):
        """Initialize variables"""
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self.__configurationManager = ConfigurationManager()

    def create_tickets(self, tickets):
        for ticket in tickets:
            self.__create_ticket(ticket)

    def __create_ticket(self, ticket):
        url = f"{self.__configurationManager.topdesk_base_url}/incidents"

        payload = {
            "status": "firstLine",
            "request": "TEST new ticket API",
            "caller": {
                "dynamicName": "ecrime"
            },
            "callerBranch": {
                "id": "f0cd5bcd-4da2-4762-b49c-6cb9905e2b7d",
                "name": "Unknown",
                "timeZone": "Europe/Berlin"
            },
            "briefDescription": "[CSIS eCrime] New Ticket",
            "externalNumber": "some external number",
            "category": {
                "id": "d9e956a4-dcf9-496e-8a15-70802107924c"
            },
            "subcategory": {
                "id": "9b153755-0b31-4af3-aaee-6379fc61fa64"
            },
            "operator": {
                "id": "73467ed4-9421-4534-b603-8cf964d38723",
                "status": "operatorGroup"
            },
            "operatorGroup": {
                "id": "73467ed4-9421-4534-b603-8cf964d38723"
            },
            "callType": {
                "id": "9aa1c7f7-8c7f-501f-aef0-dac6cd3e17e4"
            },
            "entryType": {
                "id": "04ad4d05-8824-4abe-b79c-25361aedb2a7"
            },
            "processingStatus": {
                "id": "b20abac9-6114-4907-882a-9b40802abc48"
            },
            "priority": {
                "id": "e5355405-1795-4543-963d-897cf0b6ea37"
            }
        }

        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(
            url,
            auth=(self.__configurationManager.topdesk_username, self.__configurationManager.topdesk_password),
            headers=headers,
            json = payload
        )

        print(response.json())