"""
TOPdeskAPI Module
-----------------

This module provides the `TOPdeskAPI` class for interacting with the TOPdesk API.

The class:
- Implements a Singleton pattern to ensure only one instance is created.
- Provides methods to create, update, and add actions to TOPdesk incidents.
- Uses `ConfigurationManager` to retrieve API credentials.
- Logs API requests using `Logger`.
- Evaluates HTTP responses using `HTTPRequestResponseEvaluator`.

Usage Example:
--------------
    from topdesk_api import TOPdeskAPI

    topdesk = TOPdeskAPI()

    # Create tickets in TOPdesk
    tickets = [{"title": "Example Ticket", "description": "This is a test ticket"}]
    response = topdesk.create_tickets(tickets)

    # Update existing tickets
    updates = {"TICKET_ID": {"payload": {"status": "resolved"}, "comments": [{"text": "Issue fixed"}]}}
    topdesk.update_tickets(updates)
"""

import requests
from src.config.ConfigurationManager import ConfigurationManager
from src.utils.HTTPRequestResponseEvaluator import HTTPRequestResponseEvaluator
from src.utils.Logger import Logger
from src.API.RequestType import RequestType


class TOPdeskAPI:
    """
    A Singleton class for interacting with the TOPdesk API.

    Features:
    - Creates new tickets via POST requests.
    - Updates tickets via PATCH requests.
    - Adds comments/actions via PUT requests.
    - Logs requests and responses.
    - Evaluates HTTP responses and stops execution on failure.

    Attributes:
        _instance (TOPdeskAPI): Singleton instance of the class.
        __configurationManager (ConfigurationManager): Instance for retrieving API credentials.
        __logger (Logger): Logger instance for recording API interactions.
        __responseEvaluator (HTTPRequestResponseEvaluator): Instance for evaluating HTTP responses.

    Methods:
        create_tickets(tickets: list) -> list:
            Sends POST requests to create multiple tickets.

        update_tickets(tickets: dict):
            Sends PATCH and PUT requests to update tickets and add comments.

    Private Methods:
        __create_ticket(ticket: dict) -> dict:
            Sends a POST request to create a single ticket.

        __update_ticket(topdesk_id: str, payload: dict):
            Sends a PATCH request to update a ticket's status or details.

        __update_actions(topdesk_id: str, comment: dict):
            Sends a PUT request to add an action/comment to a ticket.
    """

    _instance = None  # Singleton instance

    def __new__(cls):
        """
        Ensures only one instance of the class exists (Singleton pattern).

        Returns:
            TOPdeskAPI: The singleton instance.
        """
        if cls._instance is None:
            cls._instance = super(TOPdeskAPI, cls).__new__(cls)
            cls._instance.__initialize()
        return cls._instance

    def __initialize(self):
        """
        Initializes API credentials, logging, and response evaluation.

        This ensures that the required dependencies are set up correctly.
        """
        if not hasattr(self, "_initialized"):
            self._initialized = True

            self.__configurationManager = ConfigurationManager()
            self.__logger = Logger()
            self.__responseEvaluator = HTTPRequestResponseEvaluator()

            self.__headers = {
                "Content-Type": "application/json"
            }

    def create_tickets(self, tickets):
        """
        Sends POST requests to create multiple tickets in TOPdesk.

        Args:
            tickets (list): A list of ticket dictionaries to be created.

        Returns:
            list: A list of created ticket responses from TOPdesk.
        """
        created_tickets = []
        for ticket in tickets:
            created_tickets.append(self.__create_ticket(ticket))
        return created_tickets

    def update_tickets(self, tickets):
        """
        Sends PATCH and PUT requests to update tickets and add comments.

        Args:
            tickets (dict): A dictionary where:
                - Keys are TOPdesk ticket IDs.
                - Values contain "payload" (ticket updates) and "comments" (list of comments).
        """
        if len(tickets) == 0:
            return

        for topdesk_id, ticket_data in tickets.items():
            if "payload" not in ticket_data:
                self.__logger.warning(f"No payload for ticket ID {topdesk_id}")
                continue

            payload = ticket_data["payload"]
            self.__update_ticket(topdesk_id, payload)

            if "comments" in ticket_data:
                comments = ticket_data["comments"]

                for comment in comments:
                    self.__update_actions(topdesk_id, comment)

    def __create_ticket(self, ticket):
        """
        Sends a POST request to create a single ticket in TOPdesk.

        Args:
            ticket (dict): The ticket data to be sent.

        Returns:
            dict: The response data of the created ticket.
        """
        return self.__make_request(payload=ticket, request_type=RequestType.POST)

    def __update_ticket(self, topdesk_id, payload):
        """
        Sends a PATCH request to update a ticket's status or details.

        Args:
            topdesk_id (str): The ID of the TOPdesk ticket to update.
            payload (dict): The data to update the ticket with.
        """
        self.__make_request(payload=payload, request_type=RequestType.PATCH, endpoint=f"/number/{topdesk_id}")

    def __update_actions(self, topdesk_id, comment):
        """
        Sends a PUT request to add an action or comment to a ticket.

        Args:
            topdesk_id (str): The ID of the TOPdesk ticket to update.
            comment (dict): The comment data to add to the ticket.
        """
        self.__make_request(payload=comment, request_type=RequestType.PUT, endpoint=f"/number/{topdesk_id}")

    def __make_request(self, payload, request_type: RequestType, endpoint: str = ""):
        """
            Makes an HTTP request to the TOPdesk API with the specified request type.

            Args:
                payload (dict): The JSON payload to send in the request body.
                request_type (RequestType): The type of HTTP request (POST, PATCH, or PUT).
                endpoint (str, optional): Additional URL path to append to the incidents endpoint.
                                          Defaults to an empty string.

            Returns:
                dict: The JSON response from the API.

            Raises:
                SystemExit: If an unsupported request type is provided.
        """
        # Construct request parameters
        request_params = {
            "url": f"{self.__configurationManager.topdesk_base_url}/incidents{endpoint}",
            "auth": (self.__configurationManager.topdesk_username, self.__configurationManager.topdesk_password),
            "headers": self.__headers,
            "json": payload
        }

        # Log the request attempt
        self.__logger.info(f"Performing a {request_type.value} request at {request_params['url']}")

        # Perform the appropriate HTTP request based on the request type
        match request_type:
            case RequestType.POST:
                response = requests.post(**request_params)

            case RequestType.PUT:
                response = requests.put(**request_params)

            case RequestType.PATCH:
                response = requests.patch(**request_params)

            case _: # Handle invalid request types
                raise SystemExit

        # Evaluate the response (this may log errors and raise exceptions if necessary)
        self.__responseEvaluator.evaluate(response)

        # Return the parsed JSON response
        return response.json()
