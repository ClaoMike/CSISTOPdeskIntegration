from ConfigurationManager import ConfigurationManager
from CsisAPI import CsisAPI
from TOPdeskAPI import TOPdeskAPI
from src.TimestampUtils import TimestampUtils
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

# now = datetime.utcnow().replace(tzinfo=timezone.utc)
# now_as_azure_string = datetime_to_ms_timestamp(now)
# automationassets.set_automation_variable("CSIS_LAST_UPDATES_TIMESTAMP", now_as_azure_string)

# Convert CSIS updated tickets to TOPdesk format
# tickets_to_be_updated = ticketConverter.convert_updated_tickets_to_TOPdesk_format(tickets_to_be_updated)

# Push updates to TOPdesk'';'
# topdeskAPI.update_tickets(tickets_to_be_updated)
########################################################################################################################