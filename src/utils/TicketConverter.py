"""
TicketConverter Module
----------------------

This module defines the `TicketConverter` class, which is responsible for converting tickets
from the CSIS format to the TOPdesk format. It ensures proper mappings for:
- Ticket status
- Ticket priority
- Ticket attributes and structure

The class follows the Singleton pattern to ensure only one instance exists.

Usage Example:
--------------
    from ticket_converter import TicketConverter

    converter = TicketConverter()

    # Convert tickets to be created in TOPdesk format
    formatted_tickets = converter.convert_tickets_to_be_created_to_TOPdesk_format(csis_tickets)

    # Convert updated tickets to TOPdesk format
    updated_tickets = converter.convert_updated_tickets_to_TOPdesk_format(updated_csis_tickets)
"""
from src.utils.Logger import Logger


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
            self.__logger = Logger()

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
                self.__logger.warning(f"Ticket {ticket} is missing some fields! Please Investigate!")
                continue

            new_ticket = {
                "status": "firstLine",  # Default status for new tickets
                "request": ticket["description"],  # Full description
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
                    "id": self.__convert_csis_to_topdesk_status(ticket["status"])
                },
                "priority": {
                    "id": self.__convert_severity_to_priority(ticket["severity"])
                }
            }

            new_tickets.append(new_ticket)

        return new_tickets

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
                "processingStatus": {
                    "id": self.__convert_csis_to_topdesk_status(payload["status"])
                },
                "priority": {
                    "id": self.__convert_severity_to_priority(payload["severity"])
                }
            }

            new_comments = []
            for comment in comments:
                new_comment = {
                    "action": f"<b>Creator:</b> {comment['creator']}<br>{comment['text']}"
                }
                new_comments.append(new_comment)

            new_comments.reverse()  # Reverse to maintain chronological order
            new_tickets[payload["customer_reference"]] = {
                "payload": new_payload,
                "comments": new_comments
            }

        return new_tickets

    def __convert_severity_to_priority(self, severity):
        """
        Maps CSIS severity levels to TOPdesk priority IDs.

        Args:
            severity (str): CSIS severity level.

        Returns:
            str: Corresponding TOPdesk priority ID.
        """
        match severity:
            case "na" | "false-positive" | "info" | "medium":  # Normal priority
                return "e5355405-1795-4543-963d-897cf0b6ea37"
            case "low":  # Low priority
                return "f4f41126-f799-4517-a1a9-0f6c2d4db677"
            case "high":  # High priority
                return "3702a267-fc6d-46c9-9a4e-5b834aa6ed4d"
            case "critical":  # Critical priority
                return "106aac53-8a26-421a-b954-5d0fdc34d78a"
            case _:
                return "e5355405-1795-4543-963d-897cf0b6ea37"  # Default normal priority

    def __convert_csis_to_topdesk_status(self, status):
        """
        Maps CSIS status values to TOPdesk processing status IDs.

        Args:
            status (str): CSIS ticket status.

        Returns:
            str: Corresponding TOPdesk processing status ID.
        """
        match status:
            case "new":  # Registered
                return "b20abac9-6114-4907-882a-9b40802abc48"
            case "pending-customer":  # In Progress
                return "a4515d1f-a690-421a-b8a5-95ac9c32890e"
            case "pending-csis":  # Waiting for external input
                return "438ab0fe-819e-47fd-a5ff-1aef4271f4bd"
            case "closed":  # Closed
                return "dcc7e8ec-87e8-4fe9-b119-44f3417ed3b7"
            case _:
                return "b20abac9-6114-4907-882a-9b40802abc48"  # Default: Registered
