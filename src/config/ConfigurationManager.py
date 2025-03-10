import os
from dotenv import load_dotenv

class ConfigurationManager:
    _instance = None  # Class variable to store the single instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigurationManager, cls).__new__(cls)
            cls._instance.__initialize()  # Call internal initialization
        return cls._instance

    def __initialize(self):
        """This method initializes attributes only once."""
        if not hasattr(self, "_initialized"):  # Ensure it's only initialized once
            load_dotenv()

            # General variables
            self.__minutes = 6

            # CSIS variables
            self.__CSIS_AUTHENTICATION_URL = "https://login.csis.com/oauth2/v2/token"
            self.__CSIS_BASE_URL = "https://api.csis.com/tickets/1.0"
            self.__CSIS_CLIENT_ID = os.getenv("CSIS_CLIENT_ID")
            self.__CSIS_CLIENT_SECRET = os.getenv("CSIS_CLIENT_SECRET")
            self.__CSIS_CLIENT_TOKEN = ""

            # TOPdesk variables
            # self.__TOPdesk_BASE_URL = "https://dlfseeds.topdesk.net/tas/api" # PRODUCTION
            self.__TOPdesk_BASE_URL = "https://dlfseeds-test.topdesk.net/tas/api" # TEST

            self.__TOPdesk_USERNAME = os.getenv("TOPDESK_USERNAME")
            self.__TOPdesk_PASSWORD = os.getenv("TOPDESK_PASSWORD")

    # General variables getters and setters
    @property
    def minutes(self):
        """Getter for minutes."""
        return self.__minutes

    # CSIS variables getters and setters
    @property
    def csis_authentication_url(self):
        """Getter for __AUTHENTICATION_URL."""
        return self.__CSIS_AUTHENTICATION_URL

    @property
    def csis_base_url(self):
        """Getter for __BASE_URL."""
        return self.__CSIS_BASE_URL

    @property
    def csis_client_id(self):
        """Getter for __CLIENT_ID."""
        return self.__CSIS_CLIENT_ID

    @property
    def csis_client_secret(self):
        """Getter for __CLIENT_SECRET."""
        return self.__CSIS_CLIENT_SECRET

    @property
    def csis_client_token(self):
        """Getter for __CLIENT_TOKEN."""
        return self.__CSIS_CLIENT_TOKEN

    @csis_client_token.setter
    def csis_client_token(self, new_data):
        """Setter for __CLIENT_TOKEN."""
        if isinstance(new_data, str):
            self.__CSIS_CLIENT_TOKEN = new_data
        else:
            raise ValueError("Configuration data must be a dictionary")

    # TOPdesk variables getters and setters
    @property
    def topdesk_base_url(self):
        """Getter for __TOPdesk_BASE_URL."""
        return self.__TOPdesk_BASE_URL

    @property
    def topdesk_username(self):
        """Getter for __TOPdesk_USERNAME."""
        return self.__TOPdesk_USERNAME

    @property
    def topdesk_password(self):
        """Getter for __TOPdesk_PASSWORD."""
        return self.__TOPdesk_PASSWORD