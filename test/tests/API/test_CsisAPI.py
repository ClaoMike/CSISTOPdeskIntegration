import pytest
from unittest.mock import patch, MagicMock
from src.API.CsisAPI import CsisAPI  # Adjust path if needed
from src.API.RequestType import RequestType  # Import the enum

@pytest.fixture
def mock_csis_api():
    """Fixture to provide a singleton CsisAPI instance with mocked dependencies."""
    with (
        patch(
            "src.config.ConfigurationManager.ConfigurationManager.__new__",
            return_value=MagicMock()) as mock_config, \
            patch(
                "src.utils.Logger.Logger.__new__",
                return_value=MagicMock()), \
            patch(
                "src.utils.HTTPRequestResponseEvaluator.HTTPRequestResponseEvaluator.__new__",
                return_value=MagicMock()), \
            patch(
                "src.utils.TimestampGenerator.TimestampGenerator.__new__",
                return_value=MagicMock()) as mock_timestamp_generator):
        # Mock ConfigurationManager
        mock_config.return_value.csis_base_url = "https://mock-csis.com"
        mock_config.return_value.csis_authentication_url = "https://mock-csis.com/auth"
        mock_config.return_value.csis_client_id = "mock_client_id"
        mock_config.return_value.csis_client_secret = "mock_client_secret"
        mock_config.return_value.csis_client_token = "mock_token"
        mock_config.return_value.minutes = 30

        # Mock TimestampGenerator
        mock_timestamp_generator.return_value.get_start_of_the_search_timestamp.return_value = "2024-03-11T00:00:00Z"
        mock_timestamp_generator.return_value.get_time_difference_between.return_value = 10  # Simulated recent comment threshold

        instance = CsisAPI()
        yield instance  # Provide the instance for test cases

# 1️⃣ Test Singleton Behavior
def test_csis_api_is_singleton(mock_csis_api):
    """Test that CsisAPI follows the Singleton pattern."""
    instance1 = CsisAPI()
    instance2 = CsisAPI()

    assert id(instance1) == id(instance2)

# 2️⃣ Test Token Retrieval
@patch("requests.post")
def test_get_token(mock_post, mock_csis_api):
    # noinspection GrazieInspection
    """Test if get_token() fetches and stores the authentication token correctly."""
    mock_post.return_value.json.return_value = {"access_token": "new_mock_token"}
    mock_post.return_value.status_code = 200

    mock_csis_api.get_token()

    # Ensure the token is updated in ConfigurationManager
    assert mock_csis_api._CsisAPI__configurationManager.csis_client_token == "new_mock_token"
    mock_post.assert_called_once_with(
        "https://mock-csis.com/auth",
        data={
            "grant_type": "client_credentials",
            "client_id": "mock_client_id",
            "client_secret": "mock_client_secret",
            "scope": "https://api.csis.com/ticket:read https://api.csis.com/ticket:write"
        }
    )

@patch.object(CsisAPI, "_CsisAPI__get_filtered_tickets")
def test_get_tickets_to_be_created(mock_get_filtered_tickets, mock_csis_api):
    # noinspection GrazieInspection
    """Test if get_tickets_to_be_created() correctly fetches new tickets."""
    mock_get_filtered_tickets.return_value = [{"id": "123", "number": "TICKET-123"}]

    tickets = mock_csis_api.get_tickets_to_be_created()

    assert tickets == [{"id": "123", "number": "TICKET-123"}]
    mock_get_filtered_tickets.assert_called_once_with(
        mock_csis_api._CsisAPI__get_tickets_with_offset,
        should_have_customer_reference=False
    )

@patch.object(CsisAPI, "_CsisAPI__get_filtered_tickets")
@patch.object(CsisAPI, "_CsisAPI__attach_comments")
def test_get_updated_tickets(mock_attach_comments, mock_get_filtered_tickets, mock_csis_api):
    # noinspection GrazieInspection
    """Test if get_updated_tickets() fetches tickets and attaches comments."""
    mock_get_filtered_tickets.return_value = [{"id": "456", "number": "TICKET-456"}]
    mock_attach_comments.return_value = [{"id": "456", "number": "TICKET-456", "comments": ["Test comment"]}]

    tickets = mock_csis_api.get_updated_tickets()

    assert tickets == [{"id": "456", "number": "TICKET-456", "comments": ["Test comment"]}]
    mock_get_filtered_tickets.assert_called_once_with(
        mock_csis_api._CsisAPI__get_updated_tickets_with_offset,
        should_have_customer_reference=True
    )
    mock_attach_comments.assert_called_once()

@patch.object(CsisAPI, "_CsisAPI__make_request")
def test_update_tickets(mock_make_request, mock_csis_api):
    """Test if update_tickets() correctly updates ticket customer references."""
    tickets = [{"number": "TICKET-789", "externalNumber": "789"}]

    mock_csis_api.update_tickets(tickets)

    mock_make_request.assert_called_once_with(
        request_type=RequestType.PATCH,  # Use the actual enum instead of accessing annotations
        payload={"customer_reference": "TICKET-789"},
        endpoint="/789"
    )

@patch.object(CsisAPI, "_CsisAPI__make_request")
def test_get_ticket(mock_make_request, mock_csis_api):
    """Test if __get_ticket() correctly fetches ticket details."""
    mock_make_request.return_value = {"payload": {"id": "123", "number": "TICKET-123"}}

    response = mock_csis_api._CsisAPI__get_ticket("123")

    assert response == {"payload": {"id": "123", "number": "TICKET-123"}}
    mock_make_request.assert_called_once_with(
        request_type=RequestType.GET,
        endpoint="/123"
    )

@patch.object(CsisAPI, "_CsisAPI__get_comments")
def test_attach_comments(mock_get_comments, mock_csis_api):
    """Test if __attach_comments() correctly filters recent comments."""
    mock_get_comments.return_value = [
        {"created": "2024-03-11T00:10:00Z", "text": "Comment 1"},
        {"created": "2024-03-10T23:50:00Z", "text": "Old Comment"}
    ]

    tickets = [{"payload": {"id": "123"}}]

    filtered_tickets = mock_csis_api._CsisAPI__attach_comments(tickets)

    assert filtered_tickets[0]["comments"] == [
        {"created": "2024-03-11T00:10:00Z", "text": "Comment 1"},
        {"created": "2024-03-10T23:50:00Z", "text": "Old Comment"}
    ]
    mock_get_comments.assert_called_once_with("123")
