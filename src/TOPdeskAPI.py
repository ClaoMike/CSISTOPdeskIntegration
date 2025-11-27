import requests
from ConfigurationManager import ConfigurationManager
from typing import Optional
from HttpResponseEvaluator import RequestType, HttpResponseEvaluator
from src.TicketConverter import TicketConverter


class TOPdeskAPI:
    _instance = None  # Singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TOPdeskAPI, cls).__new__(cls)
            cls._instance.__initialize()
        return cls._instance

    def __initialize(self):
        if not hasattr(self, "_initialized"):
            self._initialized = True

            cm = ConfigurationManager()
            self.__headers = { "Content-Type": "application/json" }
            self.__auth = (cm.topdesk_username, cm.topdesk_password)

    def create_tickets(self, tickets):
        """For each ticket, create its TOPdesk representation. For each created ticket, put its comments, if any. Then return the ids."""
        created_tickets = []
        for ticket in tickets:
            # convert CSIS to TOPdesk format
            topdesk_formatted = TicketConverter.convert_CSIS_ticket_to_be_created_to_TOPdesk_format(ticket)

            # create the TOPdesk ticket
            created_topdesk_ticket_id = self.__create_ticket(topdesk_formatted)["number"]

            # add comments, if any
            if "comments" in ticket:
                for comment in ticket["comments"]:
                    self.__update_actions(
                        created_topdesk_ticket_id,
                        TicketConverter.convert_CSIS_comment_to_TOPdesk_format(comment)
                    )

            # save the topdesk id for each csis ticket
            created_ticket = {
                "csis_id": ticket["id"],
                "topdesk_id": created_topdesk_ticket_id
            }
            created_tickets.append(created_ticket)

        return created_tickets

    def update_tickets(self, tickets):
        """Sends PATCH and PUT requests to update tickets and add comments."""
        if len(tickets) == 0:
            return

        for ticket in tickets:
            # extract TOPdesk ticket number from the CSIS ticket
            topdesk_number = ticket["customer_reference"]
            # Get the TOPdesk ticket
            topdesk_current_ticket = self.__get_ticket(topdesk_number)
            # Extract the TOPdesk ticket ID
            topdesk_current_ticket_id = topdesk_current_ticket["id"]
            # Get the list of all descriptions of the TOPdesk ticket
            topdesk_current_ticket_requests = self.__get_ticket_requests(topdesk_current_ticket_id)
            # Extract the last one
            last_topdesk_description = self.__get_ticket_last_request(topdesk_current_ticket_requests)
            # check if the last description is different from the current CSIS description
            new_description = None
            current_csis_description = ticket["description"].replace('\n', '<br/>').replace('&#x20;', ' ')
            if last_topdesk_description is not None and last_topdesk_description != current_csis_description:
                new_description = current_csis_description

            # convert CSIS to TOPdesk format
            topdesk_formatted = TicketConverter.convert_updated_ticket_to_TOPdesk_format(ticket, new_description=new_description)

            self.__update_ticket(topdesk_number, topdesk_formatted)

            # add comments, if any
            if "comments" in ticket:
                for comment in ticket["comments"]:
                    self.__update_actions(
                        topdesk_number,
                        TicketConverter.convert_CSIS_comment_to_TOPdesk_format(comment)
                    )

    def __create_ticket(self, ticket):
        """Sends a POST request to create a single ticket in TOPdesk."""
        url = f"{ConfigurationManager().topdesk_base_url}/incidents"

        HttpResponseEvaluator.announce_request(url, RequestType.POST, json=ticket)
        response = requests.post(url=url, headers=self.__headers, auth=self.__auth, json=ticket)
        HttpResponseEvaluator.evaluate(response)

        return response.json()

    def __update_actions(self, topdesk_id, comment):
        """Sends a PUT request to add an action or comment to a ticket."""
        url = f"{ConfigurationManager().topdesk_base_url}/incidents/number/{topdesk_id}"

        HttpResponseEvaluator.announce_request(url, RequestType.PUT, json=comment)
        response = requests.put(url=url, headers=self.__headers, auth=self.__auth, json=comment)
        HttpResponseEvaluator.evaluate(response)

    def __get_ticket_requests(self, ticket_id: str):
        url = f"{ConfigurationManager().topdesk_base_url}/incidents/id/{ticket_id}/requests"

        HttpResponseEvaluator.announce_request(url, RequestType.GET)
        response = requests.get(url=url, headers=self.__headers, auth=self.__auth)
        HttpResponseEvaluator.evaluate(response)

        return response.json()

    def __get_ticket_last_request(self, req):
        if req is not None and len(req) != 0:
            return req[0].get("memoText")

        return None

    def __update_ticket(self, topdesk_id, payload):
        """Sends a PATCH request to update a ticket's status or details."""
        url = f"{ConfigurationManager().topdesk_base_url}/incidents/number/{topdesk_id}"

        HttpResponseEvaluator.announce_request(url, RequestType.PATCH, json=payload)
        response = requests.patch(url=url, headers=self.__headers, auth=self.__auth, json=payload)
        HttpResponseEvaluator.evaluate(response)

    def __get_ticket(self, ticket_id: str):
        """Sends a PATCH request to update a ticket's status or details."""
        url = f"{ConfigurationManager().topdesk_base_url}/incidents/number/{ticket_id}"

        HttpResponseEvaluator.announce_request(url, RequestType.GET)
        response = requests.get(url=url, headers=self.__headers, auth=self.__auth)
        HttpResponseEvaluator.evaluate(response)

        return response.json()