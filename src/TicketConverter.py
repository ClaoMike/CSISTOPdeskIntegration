class TicketConverter:
    @staticmethod
    def convert_CSIS_ticket_to_be_created_to_TOPdesk_format(ticket):
        """Converts CSIS-created ticket into the TOPdesk ticket format."""

        if {"description", "title", "id", "status", "severity"} - ticket.keys():
            print(f"Ticket {ticket} is missing some fields! Please Investigate!")
            return

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

        return new_ticket

    @staticmethod
    def convert_CSIS_comment_to_TOPdesk_format(comment):
        """Converts CSIS comment into the TOPdesk format."""
        formmated_comment = comment['text'].replace('\n', '<br>') # format
        new_comment = {
            "action": f"<b>Creator:</b> {comment['creator']}<br>{formmated_comment}"
        }

        return new_comment

    @staticmethod
    def convert_updated_ticket_to_TOPdesk_format(ticket, new_description=None):
        """Converts updated CSIS ticket into the TOPdesk format."""
        new_payload = {
            "priority": {
                "id": TicketConverter.convert_severity_to_priority(ticket["severity"])
            }
        }
        new_payload["processingStatus"] = {"id": TicketConverter.convert_csis_to_topdesk_status(ticket["status"])}

        if new_description is not None:
            new_payload["request"] = new_description  # Full description, TOPdesk does not render new line chars, but it does render break lines

        return new_payload

    @staticmethod
    def convert_severity_to_priority(severity):
        """Maps CSIS severity levels to TOPdesk priority IDs."""
        priority_map = {
            "info": "e5355405-1795-4543-963d-897cf0b6ea37",
            "low": "f4f41126-f799-4517-a1a9-0f6c2d4db677",
            "medium": "e5355405-1795-4543-963d-897cf0b6ea37",
            "high": "3702a267-fc6d-46c9-9a4e-5b834aa6ed4d",
            "critical": "106aac53-8a26-421a-b954-5d0fdc34d78a",
        }

        # Default to "normal priority" if severity not found
        return priority_map.get(severity, "e5355405-1795-4543-963d-897cf0b6ea37")

    @staticmethod
    def convert_csis_to_topdesk_status(status):
        """Maps CSIS status values to TOPdesk processing status IDs."""
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