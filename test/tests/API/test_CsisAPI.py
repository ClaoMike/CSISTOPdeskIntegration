import pytest
from unittest.mock import patch, MagicMock
from src.API.CsisAPI import CsisAPI  # Adjust path if needed

@pytest.fixture
def mock_csis_api():
    """Fixture to provide a singleton CsisAPI instance with mocked dependencies."""
    with (
        patch(
            "src.config.ConfigurationManager.ConfigurationManager.__new__",
            return_value=MagicMock()) as mock_config, \
            patch(
                "src.utils.Logger.Logger.__new__",
                return_value=MagicMock()) as mock_logger, \
            patch(
                "src.utils.HTTPRequestResponseEvaluator.HTTPRequestResponseEvaluator.__new__",
                return_value=MagicMock()) as mock_evaluator, \
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