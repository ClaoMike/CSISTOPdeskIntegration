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
        created_tickets = []
        for ticket in tickets:
            created_tickets.append(self.__create_ticket(ticket))

        return created_tickets

    def __create_ticket(self, ticket):
        url = f"{self.__configurationManager.topdesk_base_url}/incidents"

        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(
            url,
            auth=(self.__configurationManager.topdesk_username, self.__configurationManager.topdesk_password),
            headers=headers,
            json = ticket
        )

        return response.json()