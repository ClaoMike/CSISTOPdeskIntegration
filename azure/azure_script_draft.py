########################################################################################################################

from src import automationassets # dev
from abc import ABC, abstractmethod
# import automationassets # prod
from datetime import datetime, timedelta, timezone
from enum import Enum
import html
import re
import requests

########################################################################################################################

class Singleton(ABC):
    _instances = {}  # one instance per subclass

    def __new__(cls, *args, **kwargs):
        if cls is Singleton:
            raise TypeError("Singleton is abstract; subclass it instead.")

        # One instance per subclass
        if cls not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[cls] = instance
            instance._initialized = False
        return cls._instances[cls]

    def __init__(self, *args, **kwargs):
        # Only run initialization once per instance
        if getattr(self, "_initialized", False):
            return

        self._initialized = True
        self._init_singleton(*args, **kwargs)

    @abstractmethod
    def _init_singleton(self, *args, **kwargs):
        """Subclasses implement their one-time initialization here."""
        pass

########################################################################################################################

class TimestampUtils:
    @staticmethod
    def get_start_of_the_search_timestamp(minutes: int) -> str:
        """Generates a timestamp representing the current UTC time minus the specified minutes."""
        new_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        return new_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"  # Trim to 3 decimal places

    @staticmethod
    def convert_csis_time_to_UTC_z(date):
        dt = datetime.fromisoformat(date)
        dt_utc = dt.astimezone(timezone.utc)

        return dt_utc.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    @staticmethod
    def parse_ms_timestamp(ms_timestamp):
        match = re.search(r'/Date\((\d+)\)/', ms_timestamp)
        if match:
            millis = int(match.group(1))
            return datetime.fromtimestamp(millis / 1000.0, tz=timezone.utc)
        else:
            return None

    @staticmethod
    def convert_UTC_z_to_ISO8601(d):
        return datetime.fromisoformat(d.replace("Z", "+00:00"))

    @staticmethod
    def format_to_iso_z(dt):
        if dt is None:
            return None
        return dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'  # Truncate microseconds to milliseconds

    @staticmethod
    def datetime_to_ms_timestamp(dt):
        """Convert datetime (UTC) to milliseconds since epoch, in Azure's /Date(...) format"""
        epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
        millis = int((dt - epoch).total_seconds() * 1000)
        return f"/Date({millis})/"

    @staticmethod
    def parse_Azure_Date_to_iso(date):
        return TimestampUtils.format_to_iso_z(TimestampUtils.parse_ms_timestamp(date))

    @staticmethod
    def save_current_date_as(key: str):
        print(f"Saving {key} ...")
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        print(f"Current time: {now}")
        now_as_azure_string = TimestampUtils.datetime_to_ms_timestamp(now)
        automationassets.set_automation_variable(key, now_as_azure_string)

########################################################################################################################

class ConfigurationManager(Singleton):
    def _init_singleton(self):
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
        print(f"TOPdesk password: {ConfigurationManager.hide_data(self.__TOPdesk_PASSWORD)}")
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
        """Updates the CSIS client token dynamically."""
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

########################################################################################################################

class RequestType(Enum):
    POST = "POST"
    PATCH = "PATCH"
    PUT = "PUT"
    GET = "GET"

########################################################################################################################

class HttpResponseEvaluator:
    @staticmethod
    def announce_request(url, request_type: RequestType, json=None, params=None):
        print("\n## HTTP REQUEST ##")
        print(f"Performing a {request_type.value} request at {url}")
        if json is not None:
            print(f"Payload (json) {json}")
        if params is not None:
            print(f"Parameters (params) {params}")

    @staticmethod
    def evaluate(response, hide_response=False):
        if 200 <= response.status_code < 300:
            if hide_response:
                print(f"Request was successful ({response.status_code}): "
                      + f"{ConfigurationManager.hide_data(response.text)}")
            else:
                print(f"Request was successful ({response.status_code}): {response.text}")
            print("##################\n")
        else:
            print(f"Error {response.status_code}: {response.text}")
            print("##################\n")
            raise SystemExit

########################################################################################################################

class CsisAPI(Singleton):
    def _init_singleton(self):
        self.__headers = { "Content-Type": "application/json" }

    @staticmethod
    def get_token():
        """Fetches and stores the CSIS authentication token."""
        cm = ConfigurationManager()
        payload = {
            "grant_type": "client_credentials",
            "client_id": cm.csis_client_id,
            "client_secret": cm.csis_client_secret,
            "scope": "https://api.csis.com/ticket:read https://api.csis.com/ticket:write"
        }

        HttpResponseEvaluator.announce_request(cm.csis_authentication_url, RequestType.GET)
        response = requests.post(cm.csis_authentication_url, data=payload)
        HttpResponseEvaluator.evaluate(response, hide_response=True)

        return response.json().get("access_token")

    def set_authorization_token(self):
        auth_token = ConfigurationManager().csis_client_token
        print(f"Setting authorization token: {ConfigurationManager.hide_data(auth_token)}")

        self.__headers["Authorization"] = f"Bearer {auth_token}"

    def get_tickets_to_be_created(self):
        """
        Retrieves tickets that:
        - have been created after the last saved timestamp;
        - have their status set to either Pending Customer or Confirmed;
        - do not have a TOPdesk ID;
        - along with their comments;
        """
        print("Getting tickets to be created")

        # get filtered tickets
        tickets = self.__get_filtered_tickets(
            ConfigurationManager().last_new_tickets_timestamp,
            ["pending-customer", "confirmed"]
        )
        print(f"All tickets: {tickets}")

        # get their details
        tickets = self.__get_details_for_tickets(tickets)
        print(f"Detailed tickets: {tickets}")

        # filter out those that have been created in TOPdesk already
        _, tickets = self.__filter_tickets_by_customer_reference(tickets)
        print(f"Tickets without customer referene: {tickets}")

        # get comments
        for ticket in tickets:
            comments = self.__get_comments(ticket["id"])
            comments.reverse() # reverse them to display them in order of appearance in topdesk
            if comments is not None and len(comments) > 0:
                ticket["comments"] = comments

        print(f"All tickets that must be created in TOPdesk: {tickets}")

        return tickets

    def get_tickets_to_be_updated(self):
        """
        Retrieves tickets that:
        - have been updated after the last saved timestamp;
        - have their status set to either New, Pending Customer, Pending Csis, Confirmed, Closed
        - have a TOPdesk ID;
        - along with their comments;
        """
        print("Getting tickets to be updated")

        # get filtered tickets
        tickets = self.__get_filtered_tickets(
            ConfigurationManager().last_updates_timestamp,
            # "2025-12-15T00:45:00Z", # use this for testing purposes
            ["new", "pending-customer", "pending-csis", "confirmed", "closed"]
        )
        print(f"All tickets: {tickets}")

        # get their details
        tickets = self.__get_details_for_tickets(tickets)
        print(f"Detailed tickets: {tickets}")

        # filter out those that have not been created in TOPdesk already
        tickets, _ = self.__filter_tickets_by_customer_reference(tickets)
        print(f"Tickets with customer reference: {tickets}")

        # get comments
        for ticket in tickets:
            comments = self.__get_comments(ticket["id"])
            comments.reverse() # reverse them to display them in order of appearance in topdesk

            comments = self.__filter_comments_by_date(comments)
            comments = self.__filter_comments_by_creator(comments)

            if comments is not None and len(comments) > 0:
                ticket["comments"] = comments

        print(f"All tickets that must be updated in TOPdesk: {tickets}")

        return tickets

    def update_tickets_with_customer_reference(self, tickets):
        """Updates tickets with new customer references."""
        for ticket in tickets:
            payload = {
                "customer_reference": ticket["topdesk_id"],
            }

            self.__update_ticket( ticket["csis_id"], payload)

    def __filter_comments_by_date(self, comments):
        last_updated_timestamp = TimestampUtils.convert_UTC_z_to_ISO8601(ConfigurationManager().last_updates_timestamp)

        recent_comments = []
        for comment in comments:
            comment_date = TimestampUtils.convert_UTC_z_to_ISO8601(
                TimestampUtils.convert_csis_time_to_UTC_z(comment["created"])
            )

            if comment_date >= last_updated_timestamp:
                recent_comments.append(comment)

        return recent_comments

    def __filter_comments_by_creator(self, comments):
        recent_comments = []
        for comment in comments:
            if not comment["text"].startswith("[TOPdesk]"):
                recent_comments.append(comment)

        return recent_comments

    def __update_ticket(self, ticket_id, payload):
        """Updates ticket."""
        url = f"{ConfigurationManager().csis_base_url}/1.0/ticket/{ticket_id}"

        HttpResponseEvaluator.announce_request(url, RequestType.PATCH, json=payload)
        response = requests.patch(url=url, headers=self.__headers, json=payload)
        HttpResponseEvaluator.evaluate(response)

    def __get_filtered_tickets(self, updated_after, status):
        """Fetches filtered tickets, by status and update after time."""
        offset = 0
        limit = 10
        tickets = []

        url = f"{ConfigurationManager().csis_base_url}/1.1/ticket/"
        params = {
            "updated_after": updated_after,
            "status": status,
        }

        while True:
            params["offset"] = offset
            params["limit"] = limit

            HttpResponseEvaluator.announce_request(url, RequestType.GET, params=params)
            response = requests.get(url=url, headers=self.__headers, params=params)
            HttpResponseEvaluator.evaluate(response)

            payload = response.json()["payload"]

            for ticket in payload["page"]:
                tickets.append(ticket)

            if not payload.get("has_next", False):
                break

            offset += limit

        return tickets

    def __get_details_for_tickets(self, tickets):
        detailed_tickets = []
        for ticket in tickets:
            detailed_tickets.append(self.__get_ticket(ticket["id"]))

        return detailed_tickets

    def __filter_tickets_by_customer_reference(self, tickets):
        tickets_with_customer_reference     = []
        tickets_without_customer_reference  = []

        for ticket in tickets:
            if ticket.get("customer_reference") not in ("", None):
                tickets_with_customer_reference.append(ticket)
            else:
                tickets_without_customer_reference.append(ticket)

        return tickets_with_customer_reference, tickets_without_customer_reference

    def __get_ticket(self, external_id):
        """Fetches ticket details by external_id."""
        url = f"{ConfigurationManager().csis_base_url}/1.1/ticket/{external_id}"
        HttpResponseEvaluator.announce_request(url, RequestType.GET)
        response = requests.get(url=url, headers=self.__headers)
        HttpResponseEvaluator.evaluate(response)

        return response.json()["payload"]

    def __get_comments(self, ticket_id):
        """Fetches comments associated with a specific ticket."""
        url = f"{ConfigurationManager().csis_base_url}/1.0/ticket/{ticket_id}/comment"
        HttpResponseEvaluator.announce_request(url, RequestType.GET)
        response = requests.get(url=url, headers=self.__headers)
        HttpResponseEvaluator.evaluate(response)

        return response.json()["payload"]

########################################################################################################################

class StringParser:
    @staticmethod
    def normalize_html_strings(s):
        return html.unescape(s).replace('\n', '<br/>')

########################################################################################################################

class TicketConverter:
    @staticmethod
    def convert_CSIS_ticket_to_be_created_to_TOPdesk_format(ticket):
        """Converts CSIS-created ticket into the TOPdesk ticket format."""

        if {"description", "title", "id", "status", "severity"} - ticket.keys():
            print(f"Ticket {ticket} is missing some fields! Please Investigate!")
            return

        new_ticket = {
            "status": "firstLine",  # Default status for new tickets
            # Full description, TOPdesk does not render new line chars, but it does render break lines
            "request":  StringParser.normalize_html_strings(ticket["description"]),
            "caller": {
                "dynamicName": "ecrime"
            },
            "callerBranch": {
                "id": "f0cd5bcd-4da2-4762-b49c-6cb9905e2b7d",
                "name": "Unknown",
                "timeZone": "Europe/Berlin"
            },
            "briefDescription": ticket["title"][:80],  # Trim to 80 characters as required
            "externalNumber": ticket["id"],  # External reference ID
            "category": {
                "id": "d9e956a4-dcf9-496e-8a15-70802107924c"
            },
            "subcategory": {
                "id": "9b153755-0b31-4af3-aaee-6379fc61fa64"
            },
            "operator": {
                "id": "73467ed4-9421-4534-b603-8cf964d38723",
                "status": "operatorGroup"
            },
            "operatorGroup": {
                "id": "73467ed4-9421-4534-b603-8cf964d38723"
            },
            "callType": {
                "id": "9aa1c7f7-8c7f-501f-aef0-dac6cd3e17e4"
            },
            "entryType": {
                "id": "04ad4d05-8824-4abe-b79c-25361aedb2a7"
            },
            "processingStatus": {
                "id": TicketConverter.convert_csis_to_topdesk_status(ticket["status"])
            },
            "priority": {
                "id": TicketConverter.convert_severity_to_priority(ticket["severity"])
            }
        }

        return new_ticket

    @staticmethod
    def convert_CSIS_comment_to_TOPdesk_format(comment):
        """Converts CSIS comment into the TOPdesk format."""
        formmated_comment = comment['text'].replace('\n', '<br>') # format
        new_comment = {
            "action": f"<b>Creator:</b> {comment['creator']}<br>{formmated_comment}"
        }

        return new_comment

    @staticmethod
    def convert_updated_ticket_to_TOPdesk_format(ticket, new_description=None):
        """Converts updated CSIS ticket into the TOPdesk format."""
        new_payload = {
            "priority": {
                "id": TicketConverter.convert_severity_to_priority(ticket["severity"])
            }
        }
        new_payload["processingStatus"] = {"id": TicketConverter.convert_csis_to_topdesk_status(ticket["status"])}

        if new_description is not None:
            # Full description, TOPdesk does not render new line chars, but it does render break lines
            new_payload["request"] = new_description

        return new_payload

    @staticmethod
    def convert_severity_to_priority(severity):
        """Maps CSIS severity levels to TOPdesk priority IDs."""
        priority_map = {
            "info": "e5355405-1795-4543-963d-897cf0b6ea37",
            "low": "f4f41126-f799-4517-a1a9-0f6c2d4db677",
            "medium": "e5355405-1795-4543-963d-897cf0b6ea37",
            "high": "3702a267-fc6d-46c9-9a4e-5b834aa6ed4d",
            "critical": "106aac53-8a26-421a-b954-5d0fdc34d78a",
        }

        # Default to "normal priority" if severity not found
        return priority_map.get(severity, "e5355405-1795-4543-963d-897cf0b6ea37")

    @staticmethod
    def convert_csis_to_topdesk_status(status):
        """Maps CSIS status values to TOPdesk processing status IDs."""
        status_map = {
            "new": "b20abac9-6114-4907-882a-9b40802abc48", # registered
            "in-progress": "a4515d1f-a690-421a-b8a5-95ac9c32890e", # in progress
            "pending-customer": "a4515d1f-a690-421a-b8a5-95ac9c32890e", # in progress
            "pending-csis": "438ab0fe-819e-47fd-a5ff-1aef4271f4bd", # waiting external
            "confirmed": "a4515d1f-a690-421a-b8a5-95ac9c32890e", # in progress
            "closed": "dcc7e8ec-87e8-4fe9-b119-44f3417ed3b7", # closed
            # or  "e4b20e27-26bf-42e0-884a-2a4525e8ea4d", # solved
        }

        # Default: Registered
        return status_map.get(status, "b20abac9-6114-4907-882a-9b40802abc48")

########################################################################################################################

class TOPdeskAPI(Singleton):
    def _init_singleton(self):
            cm = ConfigurationManager()
            self.__headers = { "Content-Type": "application/json" }
            self.__auth = (cm.topdesk_username, cm.topdesk_password)

    def create_tickets(self, tickets):
        """
        For each ticket, create its TOPdesk representation.
        For each created ticket, put its comments, if any. Then return the ids.
        """
        created_tickets = []
        for ticket in tickets:
            # convert CSIS to TOPdesk format
            topdesk_formatted = TicketConverter.convert_CSIS_ticket_to_be_created_to_TOPdesk_format(ticket)

            # create the TOPdesk ticket
            created_topdesk_ticket_id = self.__create_ticket(topdesk_formatted)["number"]

            # add comments, if any
            if "comments" in ticket:
                for comment in ticket["comments"]:
                    self.__update_actions(
                        created_topdesk_ticket_id,
                        TicketConverter.convert_CSIS_comment_to_TOPdesk_format(comment)
                    )

            # save the topdesk id for each csis ticket
            created_ticket = {
                "csis_id": ticket["id"],
                "topdesk_id": created_topdesk_ticket_id
            }
            created_tickets.append(created_ticket)

        return created_tickets

    def update_tickets(self, tickets):
        """Sends PATCH and PUT requests to update tickets and add comments."""
        if len(tickets) == 0:
            return

        for ticket in tickets:
            # extract TOPdesk ticket number from the CSIS ticket
            topdesk_number = ticket["customer_reference"]
            # Get the TOPdesk ticket
            topdesk_current_ticket = self.__get_ticket(topdesk_number)
            # Extract the TOPdesk ticket ID
            topdesk_current_ticket_id = topdesk_current_ticket["id"]
            # Get the list of all descriptions of the TOPdesk ticket
            topdesk_current_ticket_requests = self.__get_ticket_requests(topdesk_current_ticket_id)
            # Extract the last one
            last_topdesk_description = self.__get_ticket_last_request(topdesk_current_ticket_requests)
            # check if the last description is different from the current CSIS description
            new_description = None

            current_csis_description = StringParser.normalize_html_strings(ticket["description"])
            last_topdesk_description = StringParser.normalize_html_strings(last_topdesk_description)

            print(f"TOPdesk last description: {last_topdesk_description}")
            print(f"CSIS current description: {current_csis_description}")

            if last_topdesk_description is not None and last_topdesk_description != current_csis_description:
                new_description = current_csis_description

            # convert CSIS to TOPdesk format
            topdesk_formatted = TicketConverter.convert_updated_ticket_to_TOPdesk_format(
                ticket,
                new_description=new_description
            )

            self.__update_ticket(topdesk_number, topdesk_formatted)

            # add comments, if any
            if "comments" in ticket:
                for comment in ticket["comments"]:
                    self.__update_actions(
                        topdesk_number,
                        TicketConverter.convert_CSIS_comment_to_TOPdesk_format(comment)
                    )

    def __create_ticket(self, ticket):
        """Sends a POST request to create a single ticket in TOPdesk."""
        url = f"{ConfigurationManager().topdesk_base_url}/incidents"

        HttpResponseEvaluator.announce_request(url, RequestType.POST, json=ticket)
        response = requests.post(url=url, headers=self.__headers, auth=self.__auth, json=ticket)
        HttpResponseEvaluator.evaluate(response)

        return response.json()

    def __update_actions(self, topdesk_id, comment):
        """Sends a PUT request to add an action or comment to a ticket."""
        url = f"{ConfigurationManager().topdesk_base_url}/incidents/number/{topdesk_id}"

        HttpResponseEvaluator.announce_request(url, RequestType.PUT, json=comment)
        response = requests.put(url=url, headers=self.__headers, auth=self.__auth, json=comment)
        HttpResponseEvaluator.evaluate(response)

    def __get_ticket_requests(self, ticket_id: str):
        url = f"{ConfigurationManager().topdesk_base_url}/incidents/id/{ticket_id}/requests"

        HttpResponseEvaluator.announce_request(url, RequestType.GET)
        response = requests.get(url=url, headers=self.__headers, auth=self.__auth)
        HttpResponseEvaluator.evaluate(response)

        return response.json()

    def __get_ticket_last_request(self, req):
        if req is not None and len(req) != 0:
            return req[0].get("memoText")

        return None

    def __update_ticket(self, topdesk_id, payload):
        """Sends a PATCH request to update a ticket's status or details."""
        url = f"{ConfigurationManager().topdesk_base_url}/incidents/number/{topdesk_id}"

        HttpResponseEvaluator.announce_request(url, RequestType.PATCH, json=payload)
        response = requests.patch(url=url, headers=self.__headers, auth=self.__auth, json=payload)
        HttpResponseEvaluator.evaluate(response)

    def __get_ticket(self, ticket_id: str):
        """Sends a PATCH request to update a ticket's status or details."""
        url = f"{ConfigurationManager().topdesk_base_url}/incidents/number/{ticket_id}"

        HttpResponseEvaluator.announce_request(url, RequestType.GET)
        response = requests.get(url=url, headers=self.__headers, auth=self.__auth)
        HttpResponseEvaluator.evaluate(response)

        return response.json()

########################################################################################################################
# Initialize configurations
config = ConfigurationManager()

# Initialize API handlers
csisAPI = CsisAPI()
topdeskAPI = TOPdeskAPI()

# Get CSIS Access Token
config.csis_client_token = CsisAPI.get_token()
csisAPI.set_authorization_token()
########################################################################################################################
# Identify CSIS tickets that need to be created in TOPdesk
tickets = csisAPI.get_tickets_to_be_created()
TimestampUtils.save_current_date_as(config.last_new_tickets_timestamp_key)

# Create the tickets in TOPdesk
created_tickets = topdeskAPI.create_tickets(tickets)

# Update CSIS tickets with the corresponding TOPdesk ticket IDs
csisAPI.update_tickets_with_customer_reference(created_tickets)
########################################################################################################################
# Fetch CSIS tickets that have been modified recently
tickets_to_be_updated = csisAPI.get_tickets_to_be_updated()
TimestampUtils.save_current_date_as(config.last_updates_timestamp_key)

# Push updates to TOPdesk
topdeskAPI.update_tickets(tickets_to_be_updated)
########################################################################################################################