import pytest
from unittest.mock import MagicMock, patch
from requests import Response
from src.utils.HTTPRequestResponseEvaluator import HTTPRequestResponseEvaluator
from src.utils.Logger import Logger  # Import Logger to patch it

# @pytest.fixture
# def evaluator():
#     """Fixture to create an instance of HTTPRequestResponseEvaluator."""
#     return HTTPRequestResponseEvaluator()

@pytest.fixture
def evaluator():
    """Fixture to provide a singleton evaluator instance with a mocked logger."""
    with patch.object(Logger, '__new__', return_value=MagicMock()) as mock_logger:
        instance = HTTPRequestResponseEvaluator()
        instance._HTTPRequestResponseEvaluator__logger = mock_logger  # Ensure logger is set
        yield instance  # Provide the initialized instance

def test_is_singleton_instance():
    """Test that HTTPRequestResponseEvaluator follows the Singleton pattern."""
    with patch.object(Logger, '__new__', return_value=MagicMock()):
        instance1 = HTTPRequestResponseEvaluator()
        instance2 = HTTPRequestResponseEvaluator()

    # Check if both instances have the same memory address
    assert id(instance1) == id(instance2)

def test_evaluate_success(evaluator):
    """Test `evaluate` when response is successful (2xx)."""

    # Mock response object with 200 status code
    mock_response = MagicMock(spec=Response)
    mock_response.status_code = 200
    mock_response.text = "OK"

    # Call evaluate method
    evaluator.evaluate(mock_response)

    # Ensure success is logged
    evaluator._HTTPRequestResponseEvaluator__logger.info.assert_called_once_with(
        "Request was successful! Status code: 200"
    )

def test_evaluate_failure(evaluator):
    """Test `evaluate` when response fails (non-2xx)."""

    # Mock response object with 500 status code
    mock_response = MagicMock(spec=Response)
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"

    # Expect SystemExit to be raised
    with pytest.raises(SystemExit):
        evaluator.evaluate(mock_response)

    # Ensure error logging happens before SystemExit
    evaluator._HTTPRequestResponseEvaluator__logger.error.assert_called_once_with(
        "Error 500: Internal Server Error"
    )
    evaluator._HTTPRequestResponseEvaluator__logger.close.assert_called_once()