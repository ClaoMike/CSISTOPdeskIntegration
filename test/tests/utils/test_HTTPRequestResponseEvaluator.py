import pytest
from unittest.mock import MagicMock, patch
from requests import Response
from src.utils.HTTPRequestResponseEvaluator import HTTPRequestResponseEvaluator
from src.utils.Logger import Logger  # Import Logger to patch it

@pytest.fixture
def evaluator():
    """Fixture to create an instance of HTTPRequestResponseEvaluator."""
    return HTTPRequestResponseEvaluator()

def test_is_singleton_instance():
    """Test that TimestampGenerator follows the Singleton pattern."""
    instance1 = HTTPRequestResponseEvaluator()
    instance2 = HTTPRequestResponseEvaluator()

    # Check if both instances have the same memory address
    assert id(instance1) == id(instance2)


@patch.object(Logger, "info")  # ✅ Mock the `info` method of Logger
def test_evaluate_success(mock_logger_info, evaluator):
    """Test `evaluate` when response is successful (2xx)."""

    # Mock response object with 200 status code
    mock_response = MagicMock(spec=Response)
    mock_response.status_code = 200
    mock_response.text = "OK"

    # Call evaluate method
    evaluator.evaluate(mock_response)

    # Ensure success is logged
    mock_logger_info.assert_called_once_with("Request was successful! Status code: 200")

@patch.object(Logger, "error")  # ✅ Mock the `error` method of Logger
@patch.object(Logger, "close")  # ✅ Mock the `close` method of Logger
def test_evaluate_failure(mock_logger_close, mock_logger_error, evaluator):
    """Test `evaluate` when response fails (non-2xx)."""

    # Mock response object with 500 status code
    mock_response = MagicMock(spec=Response)
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"

    # Expect SystemExit to be raised
    with pytest.raises(SystemExit):
        evaluator.evaluate(mock_response)

    # Ensure error logging happens before SystemExit
    mock_logger_error.assert_called_once_with("Error 500: Internal Server Error")
    mock_logger_close.assert_called_once()  # Ensure logger closes