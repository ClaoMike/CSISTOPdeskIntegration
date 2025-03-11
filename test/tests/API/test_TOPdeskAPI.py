import pytest
from unittest.mock import patch, MagicMock
from src.API.TOPdeskAPI import TOPdeskAPI

@pytest.fixture
def mock_topdesk_api():
    """Fixture to provide a singleton TOPdeskAPI instance with mocked dependencies."""
    with (
        patch(
            "src.config.ConfigurationManager.ConfigurationManager.__new__",
            return_value=MagicMock()) as mock_config, \
        patch(
            "src.utils.Logger.Logger.__new__",
            return_value=MagicMock()) as mock_logger, \
        patch(
            "src.utils.HTTPRequestResponseEvaluator.HTTPRequestResponseEvaluator.__new__",
            return_value=MagicMock()) as mock_evaluator):

        # Mock ConfigurationManager values
        mock_config.return_value.topdesk_base_url = "https://mock-topdesk.com"
        mock_config.return_value.topdesk_username = "mock_user"
        mock_config.return_value.topdesk_password = "mock_pass"

        instance = TOPdeskAPI()
        yield instance  # Provide the instance for test cases

# 1️⃣ Test Singleton Behavior
def test_topdesk_api_is_singleton(mock_topdesk_api):
    """Test that TOPdeskAPI follows the Singleton pattern."""
    instance1 = TOPdeskAPI()
    instance2 = TOPdeskAPI()

    assert id(instance1) == id(instance2)

@patch("requests.post")
def test_create_tickets_empty_list(mock_post, mock_topdesk_api):
    """Test creating tickets when given an empty list (should return empty)."""
    created_tickets = mock_topdesk_api.create_tickets([])
    assert created_tickets == []  # Should return an empty list
    mock_post.assert_not_called()  # No request should be made

# 2️⃣ Test Ticket Creation
@patch("requests.post")  # Mock network request
def test_create_tickets(mock_post, mock_topdesk_api):
    """Test if tickets are correctly sent via POST requests."""
    mock_post.return_value.json.return_value = {"id": "TICKET_001"}  # Mock API response
    mock_post.return_value.status_code = 201  # Simulate a successful request

    tickets = [{"title": "Test Ticket", "description": "Sample issue"}]
    created_tickets = mock_topdesk_api.create_tickets(tickets)

    mock_post.assert_called_once()  # Ensure a POST request was made
    assert len(created_tickets) == 1
    assert created_tickets[0]["id"] == "TICKET_001"

# 3️⃣ Test Ticket Update
@patch("requests.patch")
@patch("requests.put")
def test_update_tickets(mock_put, mock_patch, mock_topdesk_api):
    """Test if ticket updates are correctly sent via PATCH and PUT."""
    mock_patch.return_value.status_code = 200
    mock_put.return_value.status_code = 200

    updates = {
        "TICKET_001": {
            "payload": {"status": "resolved"},
            "comments": [{"text": "Issue fixed"}]
        }
    }

    mock_topdesk_api.update_tickets(updates)

    mock_patch.assert_called_once()  # Ensure PATCH request was made
    mock_put.assert_called_once()  # Ensure PUT request was made

@patch("requests.patch")
def test_update_tickets_missing_payload(mock_patch, mock_topdesk_api):
    """Test updating tickets when payload is missing."""
    updates = {
        "TICKET_002": {
            "comments": [{"text": "Still investigating"}]
        }
    }

    mock_topdesk_api.update_tickets(updates)

    mock_patch.assert_not_called()  # No PATCH request since payload is missing

@patch("requests.put")
@patch("requests.patch")
def test_update_tickets_missing_comments(mock_patch, mock_put, mock_topdesk_api):
    """Test updating tickets when comments are missing."""
    updates = {
        "TICKET_003": {
            "payload": {"status": "in progress"}
        }
    }

    mock_topdesk_api.update_tickets(updates)

    mock_patch.assert_called_once()
    mock_put.assert_not_called()

