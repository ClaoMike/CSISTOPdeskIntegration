"""
HTTPRequestResponseEvaluator Module
-----------------------------------

This module provides the `HTTPRequestResponseEvaluator` class for evaluating and logging HTTP responses.

The class:
- Implements a Singleton pattern to ensure a single instance.
- Uses a logging mechanism (`Logger` class) to log HTTP response details.
- Evaluates the status code of an HTTP response and logs or raises an error accordingly.

Usage Example:
--------------
    from requests import get
    from http_request_response_evaluator import HTTPRequestResponseEvaluator

    evaluator = HTTPRequestResponseEvaluator()
    response = get("https://example.com")

    evaluator.evaluate(response)  # Logs success or error based on response status
"""

from requests import Response


class HTTPRequestResponseEvaluator:
    """
    A Singleton class for evaluating and handling HTTP responses.

    Features:
    - Logs HTTP responses with different severity levels.
    - Stops execution if a request fails (non-2xx status codes).

    Attributes:
        _instance (HTTPRequestResponseEvaluator): Singleton instance of the class.

    Methods:
        evaluate(response: Response):
            Evaluates an HTTP response, logs the result, and stops execution on failure.
    """

    _instance = None  # Singleton instance

    def __new__(cls):
        """
        Ensures only one instance of the class exists (Singleton pattern).

        Returns:
            HTTPRequestResponseEvaluator: The singleton instance.
        """
        if cls._instance is None:
            cls._instance = super(HTTPRequestResponseEvaluator, cls).__new__(cls)
            cls._instance.__initialize()  # Call internal initialization
        return cls._instance

    def __initialize(self):
        """
        Initializes the class attributes only once.

        This ensures that logging is set up properly without duplicate instances.
        """
        if not hasattr(self, "_initialized"):
            self._initialized = True

    def evaluate(self, response: Response):
        """
        Categorizes and handles the status code of an HTTP response.

        This function:
        - Logs successful responses (2xx).
        - Logs and terminates execution for unsuccessful responses (non-2xx).

        Args:
            response (requests.Response): The HTTP response object to evaluate.

        Raises:
            SystemExit: If the status code is not in the 2xx range.
        """

        if 200 <= response.status_code < 300:
            # Log success message
            print(f"Request was successful! Status code: {response.status_code}")
        else:
            # Log error details and stop execution
            print(f"Error {response.status_code}: {response.text}")
            raise SystemExit