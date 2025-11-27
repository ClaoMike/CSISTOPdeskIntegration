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
        """
        For each ticket, create its TOPdesk representation. For each created ticket, put its comments, if any. Then return the ids.
        """
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

    def __create_ticket(self, ticket):
        """
        Sends a POST request to create a single ticket in TOPdesk.
        """
        url = f"{ConfigurationManager().topdesk_base_url}/incidents"

        HttpResponseEvaluator.announce_request(url, RequestType.POST, json=ticket)
        response = requests.post(url=url, headers=self.__headers, auth=self.__auth, json=ticket)
        HttpResponseEvaluator.evaluate(response)

        return response.json()

    def __update_actions(self, topdesk_id, comment):
        """
        Sends a PUT request to add an action or comment to a ticket.
        """
        url = f"{ConfigurationManager().topdesk_base_url}/incidents/number/{topdesk_id}"

        HttpResponseEvaluator.announce_request(url, RequestType.PUT, json=comment)
        response = requests.put(url=url, headers=self.__headers, auth=self.__auth, json=comment)
        HttpResponseEvaluator.evaluate(response)

    # def get_ticket(self, ticket_id: str):
    #     return self.__make_request(request_type=RequestType.GET, endpoint=f"/number/{ticket_id}")
    #
    # def get_ticket_requests(self, ticket_id: str):
    #     ticket = self.get_ticket(ticket_id=ticket_id)
    #     ticket_id = ticket["id"]
    #
    #     return self.__make_request(
    #         request_type=RequestType.GET,
    #         endpoint=f"/id/{ticket_id}/requests"
    #     )
    #
    # def get_ticket_last_request(self, ticket_id: str):
    #     req = self.get_ticket_requests(ticket_id=ticket_id)
    #     if req is not None and len(req) != 0:
    #         return req[0].get("memoText")
    #
    #     return None

    # def update_tickets(self, tickets):
    #     """
    #     Sends PATCH and PUT requests to update tickets and add comments.
    #
    #     Args:
    #         tickets (dict): A dictionary where:
    #             - Keys are TOPdesk ticket IDs.
    #             - Values contain "payload" (ticket updates) and "comments" (list of comments).
    #     """
    #     if len(tickets) == 0:
    #         return
    #
    #     for topdesk_id, ticket_data in tickets.items():
    #         if "payload" not in ticket_data:
    #             print(f"No payload for ticket ID {topdesk_id}")
    #             continue
    #
    #         payload = ticket_data["payload"]
    #         self.__update_ticket(topdesk_id, payload)
    #
    #         if "comments" in ticket_data:
    #             comments = ticket_data["comments"]
    #
    #             for comment in comments:
    #                 self.__update_actions(topdesk_id, comment)

    # def __update_ticket(self, topdesk_id, payload):
    #     """
    #     Sends a PATCH request to update a ticket's status or details.
    #
    #     Args:
    #         topdesk_id (str): The ID of the TOPdesk ticket to update.
    #         payload (dict): The data to update the ticket with.
    #     """
    #     self.__make_request(payload=payload, request_type=RequestType.PATCH, endpoint=f"/number/{topdesk_id}")