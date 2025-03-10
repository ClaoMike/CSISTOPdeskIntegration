"""
CsisAPI Module
--------------

This module provides the `CsisAPI` class for interacting with the CSIS API.

The class:
- Implements a Singleton pattern to ensure only one instance exists.
- Retrieves authentication tokens for API access.
- Fetches newly created and updated tickets from CSIS.
- Updates CSIS tickets with customer references.
- Retrieves and attaches recent comments to tickets.

Usage Example:
--------------
    from csis_api import CsisAPI

    csis = CsisAPI()

    # Get an authentication token
    csis.get_token()

    # Fetch new tickets to be created
    new_tickets = csis.get_tickets_to_be_created()

    # Fetch and update recently modified tickets
    updated_tickets = csis.get_updated_tickets()
    csis.update_tickets(updated_tickets)
"""

import requests
from src.config.ConfigurationManager import ConfigurationManager
from src.utils.HTTPRequestResponseEvaluator import HTTPRequestResponseEvaluator
from src.utils.Logger import Logger
from src.utils.TimestampGenerator import TimestampGenerator

class CsisAPI:
    """
        A Singleton class for interacting with the CSIS API.

        Features:
        - Fetches authentication tokens for API access.
        - Retrieves newly created and updated tickets.
        - Updates CSIS tickets with customer references.
        - Fetches and attaches recent comments to tickets.

        Attributes:
            _instance (CsisAPI): Singleton instance of the class.
            __logger (Logger): Logger instance for recording API interactions.
            __responseEvaluator (HTTPRequestResponseEvaluator): Evaluates API responses.
            __configurationManager (ConfigurationManager): Retrieves API credentials.
            __timestamp (str): The timestamp for filtering ticket queries.

        Methods:
            get_token():
                Fetches and stores the CSIS authentication token.

            get_tickets_to_be_created() -> list:
                Retrieves tickets created after a timestamp.

            get_updated_tickets() -> list:
                Retrieves updated tickets after a timestamp and attaches recent comments.

            update_tickets(tickets: list):
                Updates tickets with new customer references.

            __get_filtered_tickets(fetch_function, timestamp_key, should_have_customer_reference):
                Fetches and filters tickets based on creation or update timestamp.
        """

    _instance = None # Singleton instance

    def __new__(cls):
        """Ensures only one instance of the class exists (Singleton pattern)."""
        if cls._instance is None:
            cls._instance = super(CsisAPI, cls).__new__(cls)
            cls._instance.__initialize()
        return cls._instance

    def __initialize(self):
        """Initializes API credentials, logging, and response evaluation."""
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self.__logger = Logger()
            self.__responseEvaluator = HTTPRequestResponseEvaluator()
            self.__configurationManager = ConfigurationManager()

            # Generate timestamp for filtering tickets
            timestampGenerator = TimestampGenerator()
            self.__timestamp = timestampGenerator.get_start_of_the_search_timestamp(minutes=self.__configurationManager.minutes)
            self.__logger.info(f"Current timestamp: {self.__timestamp}")

    def get_token(self):
        """
           Fetches and stores the CSIS authentication token.
        """
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.__configurationManager.csis_client_id,
            "client_secret": self.__configurationManager.csis_client_secret,
            "scope": "https://api.csis.com/ticket:read https://api.csis.com/ticket:write"
        }

        self.__logger.info(f"Performing a POST request at {self.__configurationManager.csis_authentication_url}")
        response = requests.post(self.__configurationManager.csis_authentication_url, data=payload)
        self.__responseEvaluator.evaluate(response)

        token = response.json().get("access_token")
        self.__configurationManager.csis_client_token = token # Store the token for future API calls

    def get_tickets_to_be_created(self):
        """
        Retrieves tickets created after a timestamp that do not have a TOPdesk ID.

        Returns:
            list: A list of new tickets.
        """
        return self.__get_filtered_tickets(self.__get_tickets_with_offset, "created_after", should_have_customer_reference=False)

    def get_updated_tickets(self):
        """
        Retrieves updated tickets after a timestamp and attaches recent comments.

        Returns:
            list: A list of updated tickets with comments.
        """
        tickets = self.__get_filtered_tickets(self.__get_updated_tickets_with_offset, "updated_after", should_have_customer_reference=True)
        tickets = self.__attach_comments(tickets)

        return tickets

    def __get_tickets_with_offset(self, offset, limit):
        """
        Fetches tickets created after a timestamp, excluding closed tickets.

        Args:
            offset (int): Pagination offset for fetching tickets.
            limit (int): Number of tickets to fetch per request.

        Returns:
            dict: JSON response containing ticket data.

        Raises:
            SystemExit: If the API request fails.
        """
        return self.__get_tickets(offset, limit, "created_after",
                                  ["new", "pending-customer", "pending-csis", "confirmed"])

    def __get_updated_tickets_with_offset(self, offset, limit):
        """
        Fetches tickets that were updated after a timestamp.

        Args:
            offset (int): Pagination offset for fetching tickets.
            limit (int): Number of tickets to fetch per request.

        Returns:
            dict: JSON response containing ticket data.

        Raises:
            SystemExit: If the API request fails.
        """
        return self.__get_tickets(offset, limit, "updated_after",
                                  ["new", "pending-customer", "pending-csis", "confirmed", "closed"])

    def __get_tickets(self, offset, limit, timestamp_key, status_list):
        """
        Generic method to fetch tickets based on a timestamp filter.

        Args:
            offset (int): Pagination offset for fetching tickets.
            limit (int): Number of tickets to fetch per request.
            timestamp_key (str): The key determining filtering criteria ("created_after" or "updated_after").
            status_list (list): List of ticket statuses to include in the query.

        Returns:
            dict: JSON response containing ticket data.

        Raises:
            SystemExit: If the API request fails.
        """
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

        self.__logger.info(f"Performing a GET request at {url}")

        # Send request to fetch tickets
        response = requests.get(url, headers=headers, params=params)
        self.__responseEvaluator.evaluate(response)

        return response.json()

    def __get_filtered_tickets(self, fetch_function, timestamp_key, should_have_customer_reference):
        """
        Fetches and filters tickets based on the given fetch function.

        Args:
            fetch_function (function): The function to retrieve tickets.
            timestamp_key (str): The timestamp key for filtering.
            should_have_customer_reference (bool): Determines filtering logic.

        Returns:
            list: A list of filtered tickets.
        """
        offset = 0
        limit = 10
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

        # Only save tickets that match the required customer reference condition
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
        """
        Fetches tickets created after a timestamp, excluding closed tickets.

        Args:
            offset (int): Pagination offset for fetching tickets.
            limit (int): Number of tickets to fetch per request.

        Returns:
            dict: JSON response containing ticket data.

        Raises:
            SystemExit: If the API request fails.
        """
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

        self.__logger.info(f"Performing a GET request at {url}")

        # Send request to fetch tickets
        response = requests.get(url, headers=headers, params=params)
        self.__responseEvaluator.evaluate(response)

        return response.json()

    def __get_ticket(self, external_id):
        """
        Fetches ticket details by external_id.

        Args:
            external_id (str): The ID of the ticket.

        Returns:
            dict: The API response containing ticket details.
        """
        headers = {
            "Authorization": f"Bearer {self.__configurationManager.csis_client_token}",
            "Content-Type": "application/json"
        }

        url = f"{self.__configurationManager.csis_base_url}/ticket/{external_id}"  # Construct full API URL

        self.__logger.info(f"Performing a GET request at {url}")
        response = requests.get(url, headers=headers)
        self.__responseEvaluator.evaluate(response)

        return response.json()  # Return ticket details as JSON

    def update_tickets(self, tickets):
        """
                Updates tickets with new customer references.

                Args:
                    tickets (list): List of tickets to update.
                """
        for ticket in tickets:
            self.__update_ticket(ticket)

    def __update_ticket(self, ticket):
        """
               Updates a single ticket in CSIS.

               Args:
                   ticket (dict): Ticket data containing the external number and customer reference.
               """
        url = f"{self.__configurationManager.csis_base_url}/ticket/{ticket["externalNumber"]}"  # Construct full API URL

        payload = {
            "customer_reference": ticket["number"],
        }

        headers = {
            "Authorization": f"Bearer {self.__configurationManager.csis_client_token}",
            "Content-Type": "application/json"
        }

        self.__logger.info(f"Performing a PATCH request at {url}")
        response = requests.patch(
            url,
            headers=headers,
            json=payload
        )
        self.__responseEvaluator.evaluate(response)

    def __attach_comments(self, tickets):
        """
                Attaches recent comments to each ticket.

                Args:
                    tickets (list): List of tickets.

                Returns:
                    list: List of tickets with attached recent comments.
                """
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
        """
                Fetches comments associated with a specific ticket.

                Args:
                    ticket_id (str): The unique identifier of the ticket.

                Returns:
                    list: A list of comment entries from the ticket.

                Raises:
                    SystemExit: If the API request fails.
                """
        url = f"{self.__configurationManager.csis_base_url}/ticket/{ticket_id}/comment"

        headers = {
            "Authorization": f"Bearer {self.__configurationManager.csis_client_token}",
            "Content-Type": "application/json"
        }

        self.__logger.info(f"Performing a GET request at {url}")

        # Send request to fetch comments
        response = requests.get(
            url,
            headers=headers
        )
        self.__responseEvaluator.evaluate(response)

        # Return list of comments from API response
        return response.json()["payload"]

