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
from src.utils.Logger import Logger


class HTTPRequestResponseEvaluator:
    """
    A Singleton class for evaluating and handling HTTP responses.

    Features:
    - Logs HTTP responses with different severity levels.
    - Stops execution if a request fails (non-2xx status codes).
    - Uses the `Logger` class to store logs.

    Attributes:
        _instance (HTTPRequestResponseEvaluator): Singleton instance of the class.
        __logger (Logger): Logger instance for recording request responses.

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
            self.__logger = Logger()

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
        # PYTHON 3.10 only
        # match response.status_code:
        #     case _ if 200 <= response.status_code < 300:
        #         # Log success message
        #         self.__logger.info(f"Request was successful! Status code: {response.status_code}")
        #     case _:
        #         # Log error details and stop execution
        #         self.__logger.error(f"Error {response.status_code}: {response.text}")
        #         self.__logger.close()
        #         raise SystemExit

        if 200 <= response.status_code < 300:
            # Log success message
            self.__logger.info(f"Request was successful! Status code: {response.status_code}")
        else:
            # Log error details and stop execution
            self.__logger.error(f"Error {response.status_code}: {response.text}")
            self.__logger.close()
            raise SystemExit

