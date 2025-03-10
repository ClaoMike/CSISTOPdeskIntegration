from requests import Response
from src.utils.Logger import Logger

class HTTPRequestResponseEvaluator:
    _instance = None  # Class variable to store the single instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(HTTPRequestResponseEvaluator, cls).__new__(cls)
            cls._instance.__initialize()  # Call internal initialization
        return cls._instance

    def __initialize(self):
        """This method initializes attributes only once."""
        if not hasattr(self, "_initialized"):  # Ensure it's only initialized once
            self._initialized = True
            self.__logger = Logger()

    def evaluate(self, response: Response):
        """
            Categorizes and handles the status code of an HTTP response.

            This function checks the response's status code and logs or raises an error depending on whether the request was successful. By default, successful responses (2xx) are simply logged, but the complete response text can be logged with the 'showResponseTextIfSuccessful' parameter.

            Args:
                response (requests.Response): The response object returned from the HTTP request.

            Raises:
                SystemExit: If the status code is not in the 2xx range.
        """
        # If the request was not a success (status code != 2xx), then we halt the program
        match response.status_code:
            case _ if 200 <= response.status_code < 300:
                # Log success, optionally including the response text
                self.__logger.info(f"Request was successful! Status code: {response.status_code}")
            case _:
                self.__logger.error(f"Error {response.status_code}: {response.text}")
                self.__logger.close()
                raise SystemExit