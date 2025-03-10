"""
ConfigurationManager Module
---------------------------

This module provides a `ConfigurationManager` class that handles environment variables 
and configuration settings for both CSIS and TOPdesk.

The class:
- Implements a Singleton pattern to ensure only one instance is created.
- Loads environment variables from a `.env` file using `dotenv`.
- Stores API credentials and settings required for CSIS and TOPdesk integration.

Usage Example:
--------------
    from configuration_manager import ConfigurationManager

    config = ConfigurationManager()

    # Access configuration values
    csis_url = config.csis_base_url
    topdesk_username = config.topdesk_username
"""

import os
from dotenv import load_dotenv


class ConfigurationManager:
    """
    A Singleton class that manages configuration settings and environment variables.

    Features:
    - Loads `.env` variables using `dotenv`.
    - Stores API credentials for CSIS and TOPdesk.
    - Provides getters and setters for necessary configuration attributes.

    Attributes:
        _instance (ConfigurationManager): Singleton instance of the class.
        __minutes (int): General configuration value representing time in minutes.
        __CSIS_* (str): CSIS API authentication and base URL information.
        __TOPdesk_* (str): TOPdesk API credentials and base URL.

    Methods:
        csis_client_token (getter/setter):
            Retrieves or updates the CSIS client token.
    """

    _instance = None  # Singleton instance

    def __new__(cls):
        """
        Ensures only one instance of the class exists (Singleton pattern).

        Returns:
            ConfigurationManager: The singleton instance.
        """
        if cls._instance is None:
            cls._instance = super(ConfigurationManager, cls).__new__(cls)
            cls._instance.__initialize()  # Call internal initialization
        return cls._instance

    def __initialize(self):
        """
        Initializes configuration variables only once.

        This ensures that environment variables are loaded and API credentials 
        are stored without multiple instances being created.
        """
        if not hasattr(self, "_initialized"):
            load_dotenv()  # Load environment variables from .env file
            self._initialized = True

            # General configuration
            self.__minutes = 6  # Default time-related setting

            # CSIS API Credentials
            self.__CSIS_AUTHENTICATION_URL = "https://login.csis.com/oauth2/v2/token"
            self.__CSIS_BASE_URL = "https://api.csis.com/tickets/1.0"
            self.__CSIS_CLIENT_ID = os.getenv("CSIS_CLIENT_ID")
            self.__CSIS_CLIENT_SECRET = os.getenv("CSIS_CLIENT_SECRET")
            self.__CSIS_CLIENT_TOKEN = ""  # Token is set dynamically

            # TOPdesk API Credentials
            # Uncomment for production
            # self.__TOPdesk_BASE_URL = "https://dlfseeds.topdesk.net/tas/api" 

            self.__TOPdesk_BASE_URL = "https://dlfseeds-test.topdesk.net/tas/api"  # Test environment
            self.__TOPdesk_USERNAME = os.getenv("TOPDESK_USERNAME")
            self.__TOPdesk_PASSWORD = os.getenv("TOPDESK_PASSWORD")

    # General configuration variables
    @property
    def minutes(self):
        """Retrieves the configured number of minutes."""
        return self.__minutes

    # CSIS API Getters
    @property
    def csis_authentication_url(self):
        """Retrieves the CSIS authentication URL."""
        return self.__CSIS_AUTHENTICATION_URL

    @property
    def csis_base_url(self):
        """Retrieves the CSIS base API URL."""
        return self.__CSIS_BASE_URL

    @property
    def csis_client_id(self):
        """Retrieves the CSIS client ID from environment variables."""
        return self.__CSIS_CLIENT_ID

    @property
    def csis_client_secret(self):
        """Retrieves the CSIS client secret from environment variables."""
        return self.__CSIS_CLIENT_SECRET

    @property
    def csis_client_token(self):
        """Retrieves the CSIS client token, which is set dynamically after authentication."""
        return self.__CSIS_CLIENT_TOKEN

    @csis_client_token.setter
    def csis_client_token(self, new_token):
        """
        Updates the CSIS client token dynamically.

        Args:
            new_token (str): The new CSIS client token.

        Raises:
            ValueError: If the new token is not a string.
        """
        if isinstance(new_token, str):
            self.__CSIS_CLIENT_TOKEN = new_token
        else:
            raise ValueError("CSIS client token must be a string")

    # TOPdesk API Getters
    @property
    def topdesk_base_url(self):
        """Retrieves the TOPdesk base API URL (Test or Production)."""
        return self.__TOPdesk_BASE_URL

    @property
    def topdesk_username(self):
        """Retrieves the TOPdesk username from environment variables."""
        return self.__TOPdesk_USERNAME

    @property
    def topdesk_password(self):
        """Retrieves the TOPdesk password from environment variables."""
        return self.__TOPdesk_PASSWORD
