class TicketConverter:
    _instance = None  # Singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TicketConverter, cls).__new__(cls)
            cls._instance.__initialize()
        return cls._instance

    def __initialize(self):
        """Initialize variables"""
        if not hasattr(self, "_initialized"):
            self._initialized = True

    def convert_tickets_to_be_created_to_TOPdesk_format(self, tickets):
        new_tickets = []

        for ticket in tickets:
            ticket = ticket["payload"]

            new_ticket = {
                "status": "firstLine",
                "request": ticket["description"],
                "caller": {
                    "dynamicName": "ecrime"
                },
                "callerBranch": {
                    "id": "f0cd5bcd-4da2-4762-b49c-6cb9905e2b7d",
                    "name": "Unknown",
                    "timeZone": "Europe/Berlin"
                },
                "briefDescription": ticket["title"][:80], # [[{'message': 'briefDescription - The value for the field can only be 80 characters long.'}]]
                "externalNumber": ticket["id"],
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
                new_comment = {}
                new_comment["creator"] = comment["creator"]
                new_comment["text"] = comment["text"]
                new_comments.append(new_comment)

            new_tickets[payload["customer_reference"]] = {
                "payload": new_payload,
                "comments": new_comments
            }

        return new_tickets

    def __convert_severity_to_priority(self, severity):
        match severity:
            case "na":  # normal
                return "e5355405-1795-4543-963d-897cf0b6ea37"
            case "false-positive":  # normal
                return "e5355405-1795-4543-963d-897cf0b6ea37"
            case "info":  # normal
                return "e5355405-1795-4543-963d-897cf0b6ea37"
            case "low":  # low
                return "f4f41126-f799-4517-a1a9-0f6c2d4db677"
            case "medium":  # normal
                return "e5355405-1795-4543-963d-897cf0b6ea37"
            case "high":  # high
                return "3702a267-fc6d-46c9-9a4e-5b834aa6ed4d"
            case "critical":  # critical
                return "106aac53-8a26-421f-b954-5d0fdc34d78a"

    def __convert_csis_to_topdesk_status(self, status):
        match status:
            case "new":  # registered
                return "b20abac9-6114-4907-882a-9b40802abc48"
            case "pending-customer":  # in progress
                return "a4515d1f-a690-421a-b8a5-95ac9c32890e"
            case "pending-csis":  # waiting external
                return "438ab0fe-819e-47fd-a5ff-1aef4271f4bd"
            case "closed":  # closed
                return "dcc7e8ec-87e8-4fe9-b119-44f3417ed3b7"
            case _:
                return "b20abac9-6114-4907-882a-9b40802abc48"  # same as new
