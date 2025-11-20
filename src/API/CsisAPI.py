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
from src.utils.TimestampGenerator import TimestampGenerator
from src.API.RequestType import RequestType
from datetime import datetime

class CsisAPI:
    """
        A Singleton class for interacting with the CSIS API.

        Features:
        - Fetches authentication tokens for API access.
        - Retrieves created and updated tickets.
        - Updates CSIS tickets with customer references (TOPdesk IDs).
        - Fetches and attaches comments to tickets.

        Methods:
            get_token():
                Fetches and stores the CSIS authentication token.

            get_tickets_to_be_created() -> list:
                Retrieves tickets that recently have been updated to Pending Customer or Confirmed and,
                have not been created in TOPdesk already, after a timestamp.

            get_updated_tickets() -> list:
                Retrieves updated tickets after a timestamp and attaches recent comments.

            update_tickets(tickets: list):
                Updates tickets with new customer references.

            __get_filtered_tickets(fetch_function, timestamp_key, should_have_customer_reference):
                Fetches and filters tickets based on creation or update timestamp.
        """

    _instance = None  # Singleton instance

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
            self.__responseEvaluator = HTTPRequestResponseEvaluator()
            self.__configurationManager = ConfigurationManager()

            # Generate timestamp for filtering tickets
            timestamp_generator = TimestampGenerator()

            self.__headers = {
                "Content-Type": "application/json"
            }

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

        print(f"Performing a POST request at {self.__configurationManager.csis_authentication_url}")
        response = requests.post(self.__configurationManager.csis_authentication_url, data=payload)
        self.__responseEvaluator.evaluate(response)

        token = response.json().get("access_token")
        self.__configurationManager.csis_client_token = token  # Store the token for future API calls

        self.__headers["Authorization"] = f"Bearer {self.__configurationManager.csis_client_token}"

    def update_tickets(self, tickets):
        """
                Updates tickets with new customer references.

                Args:
                    tickets (list): List of tickets to update.
                """
        for ticket in tickets:
            payload = {
                "customer_reference": ticket["number"],
            }

            self.__make_request(
                request_type=RequestType.PATCH,
                payload=payload,
                endpoint=f"/{ticket['externalNumber']}"
            )

    def get_tickets_to_be_created(self):
        """
        Retrieves tickets created after a timestamp that do not have a TOPdesk ID.

        Returns:
            list: A list of new tickets.
        """
        tickets = self.__get_filtered_tickets(self.__get_tickets_with_offset, should_have_customer_reference=False)
        tickets = self.__attach_comments(tickets, recent=False)

        return tickets

    def get_updated_tickets(self):
        """
        Retrieves updated tickets after a timestamp and attaches recent comments.

        Returns:
            list: A list of updated tickets with comments.
        """
        tickets = self.__get_filtered_tickets(self.__get_updated_tickets_with_offset,
                                              should_have_customer_reference=True)
        tickets = self.__attach_comments(tickets)

        return tickets

    def __get_filtered_tickets(self, fetch_function, should_have_customer_reference):
        """
        Fetches and filters tickets based on the given fetch function.

        Args:
            fetch_function (function): The function to retrieve tickets.
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

        params = {
            "updated_after": self.__configurationManager.last_new_tickets_timestamp,
            # Ensure the values in { "new",  "pending-csis", "closed" } are excluded
            # As of 19/11/2025, after the latest CSIS changes, where are tickets are changed to cases,
            # and cases now include alerts and incidents.
            # we only convert to topdesk those that are Pending Customer and/or Confirmed.
            "status": ["pending-customer", "confirmed"],
            "limit": limit,
            "offset": offset
        }
        response = self.__make_request(request_type=RequestType.GET, params=params)
        print(response)

        return response

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
        params = {
            "updated_after": self.__configurationManager.last_updates_timestamp,
            "status": ["new", "pending-customer", "pending-csis", "confirmed", "closed"],
            "limit": limit,
            "offset": offset
        }

        return self.__make_request(request_type=RequestType.GET, params=params)

    def __get_ticket(self, external_id):
        """
        Fetches ticket details by external_id.

        Args:
            external_id (str): The ID of the ticket.

        Returns:
            dict: The API response containing ticket details.
        """
        return self.__make_request(request_type=RequestType.GET,
                                   endpoint=f"/{external_id}")  # Return ticket details as JSON

    def __attach_comments(self, tickets, recent=True):
        """
                Attaches recent comments to each ticket.

                Args:
                    tickets (list): List of tickets.

                Returns:
                    list: List of tickets with attached recent comments.
                """

        if recent:
            last_update = datetime.fromisoformat(
                self.__configurationManager.last_updates_timestamp.replace("Z", "+00:00")
            )

        for ticket in tickets:
            # get all comments in ticket
            all_comments = self.__get_comments(ticket["payload"]["id"])

            # save only those that are recent
            recent_comments = []
            for comment in all_comments:
                if recent:
                    comment_created = datetime.fromisoformat(comment["created"])
                comment_text = comment['text']

                if recent:
                    print(f"Last Update Timestamp: {last_update}")
                print(f"Comment timestamp: {comment_created}")

                if not comment_text.startswith("[TOPdesk]"):
                    if recent:  # if recent we filter them based on date, otherwise not
                        if last_update < comment_created:
                            recent_comments.append(comment)
                    else:
                        recent_comments.append(comment)

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
        response = self.__make_request(request_type=RequestType.GET, endpoint=f"/{ticket_id}/comment")

        # Return list of comments from API response
        return response["payload"]

    def __make_request(self, request_type: RequestType, payload=None, params=None, endpoint: str = ""):
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
            "url": f"{self.__configurationManager.csis_base_url}/ticket{endpoint}",
            "headers": self.__headers,
        }

        if payload is not None:
            request_params["json"] = payload

        if params is not None:
            request_params["params"] = params

        # Log the request attempt
        print(f"Performing a {request_type.value} request at {request_params['url']}")

        # Perform the appropriate HTTP request based on the request type
        if request_type == RequestType.POST:
            response = requests.post(**request_params)

        elif request_type == RequestType.PUT:
            response = requests.put(**request_params)

        elif request_type == RequestType.PATCH:
            response = requests.patch(**request_params)

        elif request_type == RequestType.GET:
            response = requests.get(**request_params)

        else:
            raise SystemExit("Invalid request type")

        # Evaluate the response (this may log errors and raise exceptions if necessary)
        self.__responseEvaluator.evaluate(response)

        # Return the parsed JSON response
        return response.json()
