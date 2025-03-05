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
            self.__AUTHENTICATION_URL = "https://login.csis.com/oauth2/v2/token"
            self.__BASE_URL = "https://api.csis.com/tickets/1.0"

            load_dotenv()
            self.__CLIENT_ID = os.getenv("CLIENT_ID")
            self.__CLIENT_SECRET = os.getenv("CLIENT_SECRET")

            self.__CLIENT_TOKEN = ""

    @property
    def authentication_url(self):
        """Getter for __AUTHENTICATION_URL."""
        return self.__AUTHENTICATION_URL

    @property
    def base_url(self):
        """Getter for __BASE_URL."""
        return self.__BASE_URL

    @property
    def client_id(self):
        """Getter for __CLIENT_ID."""
        return self.__CLIENT_ID

    @property
    def client_secret(self):
        """Getter for __CLIENT_SECRET."""
        return self.__CLIENT_SECRET

    @property
    def client_token(self):
        """Getter for __CLIENT_TOKEN."""
        return self.__CLIENT_TOKEN

    @client_token.setter
    def client_token(self, new_data):
        """Setter for __CLIENT_TOKEN."""
        if isinstance(new_data, str):
            self.__CLIENT_TOKEN = new_data
        else:
            raise ValueError("Configuration data must be a dictionary")