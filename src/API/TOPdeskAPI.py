import requests
from src.config.ConfigurationManager import ConfigurationManager
from src.utils.HTTPRequestResponseEvaluator import HTTPRequestResponseEvaluator
from src.utils.Logger import Logger


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
            self.__logger = Logger()
            self.__responseEvaluator = HTTPRequestResponseEvaluator()

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

        self.__logger.info(f"Performing a POST request at {url}")
        response = requests.post(
            url,
            auth=(self.__configurationManager.topdesk_username, self.__configurationManager.topdesk_password),
            headers=headers,
            json = ticket
        )
        self.__responseEvaluator.evaluate(response)

        return response.json()

    def update_tickets(self, tickets):
        for topdesk_id in tickets.keys():
            payload = tickets[topdesk_id]["payload"]
            comments = tickets[topdesk_id]["comments"]

            self.__update_ticket(topdesk_id, payload)

            for comment in comments:
                self.__update_actions(topdesk_id, comment)


    def __update_ticket(self, topdesk_id, payload):
        url = f"{self.__configurationManager.topdesk_base_url}/incidents/number/{topdesk_id}"

        headers = {
            "Content-Type": "application/json"
        }

        self.__logger.info(f"Performing a PATCH request at {url}")
        response = requests.patch(
            url,
            auth=(self.__configurationManager.topdesk_username, self.__configurationManager.topdesk_password),
            headers=headers,
            json=payload
        )
        self.__responseEvaluator.evaluate(response)

    def __update_actions(self, topdesk_id, comment):
        url = f"{self.__configurationManager.topdesk_base_url}/incidents/number/{topdesk_id}"

        headers = {
            "Content-Type": "application/json"
        }

        self.__logger.info(f"Performing a PUT request at {url}")
        response = requests.put(
            url,
            auth=(self.__configurationManager.topdesk_username, self.__configurationManager.topdesk_password),
            headers=headers,
            json=comment
        )
        self.__responseEvaluator.evaluate(response)