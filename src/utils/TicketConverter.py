class TicketConverter:
    """
    A Singleton class to convert CSIS tickets into the TOPdesk ticket format.

    Attributes:
        _instance (TicketConverter): A private class instance for Singleton behavior.

    Methods:
        convert_tickets_to_be_created_to_TOPdesk_format(tickets: list) -> list:
            Converts CSIS-created tickets into TOPdesk-compatible format.

        convert_updated_tickets_to_TOPdesk_format(tickets: list) -> dict:
            Converts CSIS-updated tickets into TOPdesk-compatible format.

    Private Methods:
        __convert_severity_to_priority(severity: str) -> str:
            Maps CSIS severity levels to TOPdesk priority IDs.

        __convert_csis_to_topdesk_status(status: str) -> str:
            Maps CSIS status values to TOPdesk processing status IDs.
    """

    _instance = None  # Singleton instance

    def __new__(cls):
        """
        Ensures only one instance of the class is created (Singleton pattern).

        Returns:
            TicketConverter: The singleton instance of the class.
        """
        if cls._instance is None:
            cls._instance = super(TicketConverter, cls).__new__(cls)
            cls._instance.__initialize()
        return cls._instance

    def __initialize(self):
        """
        Initializes the class variables. Ensures initialization happens only once.
        """
        if not hasattr(self, "_initialized"):
            self._initialized = True

    def convert_tickets_to_be_created_to_TOPdesk_format(self, tickets):
        """
        Converts CSIS-created tickets into the TOPdesk ticket format.

        Args:
            tickets (list): A list of CSIS ticket dictionaries.

        Returns:
            list: A list of dictionaries formatted for TOPdesk.
        """
        new_tickets = []

        for ticket in tickets:
            ticket = ticket["payload"]  # Extract ticket details from payload

            if {"description", "title", "id", "status", "severity"} - ticket.keys():
                print(f"Ticket {ticket} is missing some fields! Please Investigate!")
                continue

            new_ticket = {
                "status": "firstLine",  # Default status for new tickets
                "request": ticket["description"].replace('\n', '<br>'),  # Full description, TOPdesk does not render new line chars, but it does render break lines
                "caller": {
                    "dynamicName": "ecrime"
                },
                "callerBranch": {
                    "id": "f0cd5bcd-4da2-4762-b49c-6cb9905e2b7d",
                    "name": "Unknown",
                    "timeZone": "Europe/Berlin"
                },
                "briefDescription": ticket["title"][:80],  # Trim to 80 characters as required
                "externalNumber": ticket["id"],  # External reference ID
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
                    "id": TicketConverter.convert_csis_to_topdesk_status(ticket["status"])
                },
                "priority": {
                    "id": TicketConverter.convert_severity_to_priority(ticket["severity"])
                }
            }

            new_tickets.append(new_ticket)

        return new_tickets

    # noinspection PyMethodMayBeStatic
    def convert_updated_tickets_to_TOPdesk_format(self, tickets):
        """
        Converts updated CSIS tickets into the TOPdesk format.

        Args:
            tickets (list): A list of CSIS ticket dictionaries with updates.

        Returns:
            dict: A dictionary of converted tickets with their customer references.
        """
        new_tickets = {}

        for ticket in tickets:
            payload = ticket["payload"]
            comments = ticket["comments"]            

            new_payload = {
                
                "priority": {
                    "id": TicketConverter.convert_severity_to_priority(payload["severity"])
                }
            }
            new_payload["processingStatus"] = {"id": TicketConverter.convert_csis_to_topdesk_status(payload["status"])}

            # we should update the description only if it has changed
            current_csis_description = payload["description"].replace('\n', '<br/>')
            current_csis_description = current_csis_description.replace('&#x20;', ' ')

            topdesk_ticket_id = payload["customer_reference"]
            current_topdesk_description = TOPdeskAPI().get_ticket_last_request(ticket_id=topdesk_ticket_id)
            print(f"Ticket: {topdesk_ticket_id}\n\nCSIS description:\n{current_csis_description}\n\nTOPdesk description:\n{current_topdesk_description}")
            if current_csis_description != current_topdesk_description:
                print("Updating description")
                new_payload["request"] = current_csis_description  # Full description, TOPdesk does not render new line chars, but it does render break lines

            new_comments = []
            for comment in comments:
                comment['text'] = comment['text'].replace('\n', '<br>') # format
                new_comment = {
                    "action": f"<b>Creator:</b> {comment['creator']}<br>{comment['text']}"
                }
                new_comments.append(new_comment)

            new_comments.reverse()  # Reverse to maintain chronological order
            new_tickets[payload["customer_reference"]] = {
                "payload": new_payload,
                "comments": new_comments
            }

            print(new_payload)

        return new_tickets

    # noinspection PyMethodParameters
    def convert_severity_to_priority(severity):
        """
        Maps CSIS severity levels to TOPdesk priority IDs.

        Args:
            severity (str): CSIS severity level.

        Returns:
            str: Corresponding TOPdesk priority ID.
        """

        priority_map = {
            "info": "e5355405-1795-4543-963d-897cf0b6ea37",
            "low": "f4f41126-f799-4517-a1a9-0f6c2d4db677",
            "medium": "e5355405-1795-4543-963d-897cf0b6ea37",
            "high": "3702a267-fc6d-46c9-9a4e-5b834aa6ed4d",
            "critical": "106aac53-8a26-421a-b954-5d0fdc34d78a",
        }

        # Default to "normal priority" if severity not found
        return priority_map.get(severity, "e5355405-1795-4543-963d-897cf0b6ea37")

    # noinspection PyMethodParameters
    def convert_csis_to_topdesk_status(status):
        """
        Maps CSIS status values to TOPdesk processing status IDs.

        Args:
            status (str): CSIS ticket status.

        Returns:
            str: Corresponding TOPdesk processing status ID.
        """

        status_map = {
            "new": "b20abac9-6114-4907-882a-9b40802abc48", # registered
            "in-progress": "a4515d1f-a690-421a-b8a5-95ac9c32890e", # in progress
            "pending-customer": "a4515d1f-a690-421a-b8a5-95ac9c32890e", # in progress
            "pending-csis": "438ab0fe-819e-47fd-a5ff-1aef4271f4bd", # waiting external
            "confirmed": "a4515d1f-a690-421a-b8a5-95ac9c32890e", # in progress
            "closed": "dcc7e8ec-87e8-4fe9-b119-44f3417ed3b7", # closed / or  "e4b20e27-26bf-42e0-884a-2a4525e8ea4d", # solved
        }

        # Default: Registered
        return status_map.get(status, "b20abac9-6114-4907-882a-9b40802abc48")