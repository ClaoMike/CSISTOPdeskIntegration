import pytest
from unittest.mock import MagicMock, patch
from src.utils.TicketConverter import TicketConverter  # Import Logger to patch it

@pytest.fixture
def ticket_converter():
    """Fixture to provide a singleton TOPdeskAPI instance with mocked dependencies."""
    with patch("src.utils.Logger.Logger.__new__", return_value=MagicMock()) as mock_logger:

        instance = TicketConverter()
        yield instance  # Provide the instance for test cases

# 1️⃣ Test Singleton Behavior
def test_ticket_converter_is_singleton():
    """Test that TicketConverter follows the Singleton pattern."""
    with patch("src.utils.Logger.Logger.__new__", return_value=MagicMock()):
        instance1 = TicketConverter()
        instance2 = TicketConverter()

    assert id(instance1) == id(instance2)

# 2️⃣ Test Ticket Creation Conversion
def test_convert_tickets_to_be_created_to_TOPdesk_format(ticket_converter):
    """Test if tickets are correctly converted to the TOPdesk format."""
    id = "12345"
    description = "This is a test ticket description."

    title = "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum."
    trimmed_title = "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem"

    csis_tickets = [
        {
            "payload": {
                "id": id,
                "title": title,
                "description": description,
                "status": "new",
                "severity": "high"
            }
        }
    ]

    converted_tickets = ticket_converter.convert_tickets_to_be_created_to_TOPdesk_format(csis_tickets)

    assert len(converted_tickets) == 1
    assert converted_tickets[0]["request"] == description
    assert converted_tickets[0]["briefDescription"] == trimmed_title # at most 80 characters on the title!
    assert converted_tickets[0]["externalNumber"] == id

    assert converted_tickets[0]["processingStatus"]["id"] == "b20abac9-6114-4907-882a-9b40802abc48"  # "new" → "Registered"
    assert converted_tickets[0]["priority"]["id"] == "3702a267-fc6d-46c9-9a4e-5b834aa6ed4d"  # "high" → High priority

    csis_tickets[0]["payload"]["status"] = "pending-customer"
    csis_tickets[0]["payload"]["severity"] = "critical"
    converted_tickets = ticket_converter.convert_tickets_to_be_created_to_TOPdesk_format(csis_tickets)

    assert converted_tickets[0]["processingStatus"]["id"] == "a4515d1f-a690-421a-b8a5-95ac9c32890e"  # "pending-customer" → "In Progress"
    assert converted_tickets[0]["priority"]["id"] == "106aac53-8a26-421a-b954-5d0fdc34d78a"  # "critical" → Critical priority

    csis_tickets[0]["payload"]["status"] = "pending-csis"
    csis_tickets[0]["payload"]["severity"] = "low"
    converted_tickets = ticket_converter.convert_tickets_to_be_created_to_TOPdesk_format(csis_tickets)

    assert converted_tickets[0]["processingStatus"]["id"] == "438ab0fe-819e-47fd-a5ff-1aef4271f4bd"  # "pending-csis" → "Waiting for external"
    assert converted_tickets[0]["priority"]["id"] == "f4f41126-f799-4517-a1a9-0f6c2d4db677"  # "low" → Low priority

    csis_tickets[0]["payload"]["status"] = "closed"
    csis_tickets[0]["payload"]["severity"] = "medium"
    converted_tickets = ticket_converter.convert_tickets_to_be_created_to_TOPdesk_format(csis_tickets)

    assert converted_tickets[0]["processingStatus"]["id"] == "dcc7e8ec-87e8-4fe9-b119-44f3417ed3b7"  # "closed" → "Closed"
    assert converted_tickets[0]["priority"]["id"] == "e5355405-1795-4543-963d-897cf0b6ea37"  # "medium" → Normal priority

    csis_tickets[0]["payload"]["severity"] = "info"
    converted_tickets = ticket_converter.convert_tickets_to_be_created_to_TOPdesk_format(csis_tickets)

    assert converted_tickets[0]["priority"]["id"] == "e5355405-1795-4543-963d-897cf0b6ea37"  # "info" → Normal priority

    csis_tickets[0]["payload"]["severity"] = "false-positive"
    converted_tickets = ticket_converter.convert_tickets_to_be_created_to_TOPdesk_format(csis_tickets)

    assert converted_tickets[0]["priority"][
               "id"] == "e5355405-1795-4543-963d-897cf0b6ea37"  # "false-positive" → Normal priority

    csis_tickets[0]["payload"]["severity"] = "na"
    converted_tickets = ticket_converter.convert_tickets_to_be_created_to_TOPdesk_format(csis_tickets)

    assert converted_tickets[0]["priority"][
               "id"] == "e5355405-1795-4543-963d-897cf0b6ea37"  # "na" → Normal priority


# 4️⃣ Test Edge Cases (Missing Fields)
def test_convert_tickets_missing_fields(ticket_converter):
    """Test conversion with missing fields in ticket data."""
    csis_tickets = [
        {"payload": {"id": "67890", "title": "Missing Fields Test", "status": "unknown_status"}}
    ]
    converted_tickets = ticket_converter.convert_tickets_to_be_created_to_TOPdesk_format(csis_tickets)

    assert len(converted_tickets) == 0

# 3️⃣ Test Updated Ticket Conversion
def test_convert_updated_tickets_to_TOPdesk_format(ticket_converter):
    """Test if updated CSIS tickets are correctly converted."""
    csis_updated_tickets = [
        {
            "payload": {
                "customer_reference": "54321",
                "status": "closed",
                "severity": "critical"
            },
            "comments": [
                {"creator": "John Doe", "text": "Initial issue reported."},
                {"creator": "Jane Smith", "text": "Issue resolved."}
            ]
        }
    ]

    converted_tickets = ticket_converter.convert_updated_tickets_to_TOPdesk_format(csis_updated_tickets)

    assert "54321" in converted_tickets
    assert converted_tickets["54321"]["payload"]["processingStatus"]["id"] == "dcc7e8ec-87e8-4fe9-b119-44f3417ed3b7"  # "closed" → "Closed"
    assert converted_tickets["54321"]["payload"]["priority"]["id"] == "106aac53-8a26-421a-b954-5d0fdc34d78a"  # "critical" → Critical priority

    # Check that comments are reversed
    assert converted_tickets["54321"]["comments"][0]["action"] == "<b>Creator:</b> Jane Smith<br>Issue resolved."
    assert converted_tickets["54321"]["comments"][1]["action"] == "<b>Creator:</b> John Doe<br>Initial issue reported."