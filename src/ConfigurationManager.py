import automationassets
import re
from datetime import datetime, timezone

def parse_ms_timestamp(ms_timestamp):
    match = re.search(r'/Date\((\d+)\)/', ms_timestamp)
    if match:
        millis = int(match.group(1))
        return datetime.fromtimestamp(millis / 1000.0, tz=timezone.utc)
    else:
        return None

def format_to_iso_z(dt):
    if dt is None:
        return None
    return dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'  # Truncate microseconds to milliseconds

def datetime_to_ms_timestamp(dt):
    """Convert datetime (UTC) to milliseconds since epoch, in Azure's /Date(...) format"""
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    millis = int((dt - epoch).total_seconds() * 1000)
    return f"/Date({millis})/"

def hide_data(s: str) -> str:
    return re.sub(r'.', '*', s)

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
            self.__LAST_NEW_TICKETS_TIMESTAMP = format_to_iso_z(
                parse_ms_timestamp(automationassets.get_automation_variable("CSIS_LAST_NEW_TICKETS_TIMESTAMP")))
            self.__LAST_UPDATES_TIMESTAMP = format_to_iso_z(
                parse_ms_timestamp(automationassets.get_automation_variable("CSIS_LAST_UPDATES_TIMESTAMP")))
            minutes_str = automationassets.get_automation_variable("CSIS_MINUTES")
            self.__minutes = int(minutes_str)

            # CSIS data
            self.__CSIS_AUTHENTICATION_URL = "https://login.csis.com/oauth2/v2/token"
            self.__CSIS_BASE_URL = "https://api.csis.com/tickets/1.0"
            self.__CSIS_CLIENT_ID = automationassets.get_automation_variable("CSIS_CLIENT_ID")
            self.__CSIS_CLIENT_SECRET = automationassets.get_automation_variable("CSIS_CLIENT_SECRET")
            self.__CSIS_CLIENT_TOKEN = ""  # Token is set dynamically

            # TOPdesk data
            cred = automationassets.get_automation_credential("CREDENTIAL_TOPDESK_API")
            self.__TOPdesk_USERNAME = cred["username"]
            self.__TOPdesk_PASSWORD = cred["password"]
            self.__TOPdesk_BASE_URL = "https://dlfseeds.topdesk.net/tas/api"

            # Logs
            print(f"Last new tickets timestamp: {self.__LAST_NEW_TICKETS_TIMESTAMP}")
            print(f"Last updates timestamp: {self.__LAST_UPDATES_TIMESTAMP}")
            print(f"MINUTES: {self.__minutes}")
            print(f"CSIS authentication url: {self.__CSIS_AUTHENTICATION_URL}")
            print(f"CSIS base url: {self.__CSIS_BASE_URL}")
            print(f"CSIS client ID: {hide_data(self.__CSIS_CLIENT_ID)}")
            print(f"CSIS client secret: {hide_data(self.__CSIS_CLIENT_SECRET)}")
            print(f"TOPdesk username: {self.__TOPdesk_USERNAME}")
            print(f"TOPdesk password: {self.__TOPdesk_PASSWORD}")
            print(f"TOPdesk base url: {self.__TOPdesk_BASE_URL}")

            print("Script configuration loaded successfully.")

    @property
    def last_new_tickets_timestamp(self):
        """Retrieves the value of the last fetch of new created tickets."""
        return self.__LAST_NEW_TICKETS_TIMESTAMP

    @property
    def last_updates_timestamp(self):
        """Retrieves the value of the last fetch of new updates."""
        return self.__LAST_UPDATES_TIMESTAMP

    @property
    def is_logging(self):
        """Retrieves the value of the logging status."""
        return self.__is_logging

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