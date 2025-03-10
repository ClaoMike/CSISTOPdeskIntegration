import requests
from src.config.ConfigurationManager import ConfigurationManager

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

    def update_tickets(self, tickets):
        for topdesk_id in tickets.keys():
            url = f"{self.__configurationManager.topdesk_base_url}/incidents/number/{topdesk_id}"

            headers = {
                "Content-Type": "application/json"
            }

            response = requests.patch(
                url,
                auth=(self.__configurationManager.topdesk_username, self.__configurationManager.topdesk_password),
                headers=headers,
                json=tickets[topdesk_id]
            )

    def __update_ticket(self, ticket_id, ticket):
        pass

    def __update_actions(self, ticket_id, actions):
        pass