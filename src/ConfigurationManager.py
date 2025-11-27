import automationassets
import re
from TimestampUtils import TimestampUtils

class ConfigurationManager:
    _instance = None  # Singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigurationManager, cls).__new__(cls)
            cls._instance.__initialize()  # Call internal initialization
        return cls._instance

    def __initialize(self):
        if not hasattr(self, "_initialized"):
            self._initialized = True

            print("Preparing script configuration...")

            # General configuration
            self.__LAST_NEW_TICKETS_TIMESTAMP_KEY   = "CSIS_LAST_NEW_TICKETS_TIMESTAMP"
            self.__LAST_UPDATES_TIMESTAMP_KEY       = "CSIS_LAST_UPDATES_TIMESTAMP"

            self.__LAST_NEW_TICKETS_TIMESTAMP = TimestampUtils.parse_Azure_Date_to_iso(
                automationassets.get_automation_variable(self.__LAST_NEW_TICKETS_TIMESTAMP_KEY)
            )
            self.__LAST_UPDATES_TIMESTAMP = TimestampUtils.parse_Azure_Date_to_iso(
                automationassets.get_automation_variable("CSIS_LAST_UPDATES_TIMESTAMP")
            )

            # CSIS data
            self.__CSIS_AUTHENTICATION_URL  = "https://login.csis.com/oauth2/v2/token"
            self.__CSIS_BASE_URL            = "https://api.csis.com/tickets"
            self.__CSIS_CLIENT_ID           = automationassets.get_automation_variable("CSIS_CLIENT_ID")
            self.__CSIS_CLIENT_SECRET       = automationassets.get_automation_variable("CSIS_CLIENT_SECRET")
            self.__CSIS_CLIENT_TOKEN        = ""

            # TOPdesk data
            cred                    = automationassets.get_automation_credential("CREDENTIAL_TOPDESK_API")
            self.__TOPdesk_USERNAME = cred["username"]
            self.__TOPdesk_PASSWORD = cred["password"]
            self.__TOPdesk_BASE_URL = "https://dlfseeds.topdesk.net/tas/api"

            # Logs
            print(f"Last new tickets timestamp: {self.__LAST_NEW_TICKETS_TIMESTAMP}")
            print(f"Last updates timestamp: {self.__LAST_UPDATES_TIMESTAMP}")
            print(f"CSIS authentication url: {self.__CSIS_AUTHENTICATION_URL}")
            print(f"CSIS base url: {self.__CSIS_BASE_URL}")
            print(f"CSIS client ID: {ConfigurationManager.hide_data(self.__CSIS_CLIENT_ID)}")
            print(f"CSIS client secret: {ConfigurationManager.hide_data(self.__CSIS_CLIENT_SECRET)}")
            print(f"TOPdesk username: {self.__TOPdesk_USERNAME}")
            print(f"TOPdesk password: {self.__TOPdesk_PASSWORD}")
            print(f"TOPdesk base url: {self.__TOPdesk_BASE_URL}")

            print("Script configuration loaded successfully.")

    @property
    def last_new_tickets_timestamp(self):
        """Retrieves the value of the last fetch of new created tickets."""
        return self.__LAST_NEW_TICKETS_TIMESTAMP

    @property
    def last_new_tickets_timestamp_key(self):
        """Retrieves the key of the last fetch of new created tickets object in Azure automations."""
        return self.__LAST_NEW_TICKETS_TIMESTAMP_KEY

    @property
    def last_updates_timestamp(self):
        """Retrieves the value of the last fetch of new updates."""
        return self.__LAST_UPDATES_TIMESTAMP

    @property
    def last_updates_timestamp_key(self):
        """Retrieves the key of the last fetch of new updates object in Azure automations."""
        return self.__LAST_UPDATES_TIMESTAMP_KEY

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

    # noinspection PyAttributeOutsideInit
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

    @staticmethod
    def hide_data(s: str) -> str:
        return re.sub(r'.', '*', s)