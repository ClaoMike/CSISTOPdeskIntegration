from ConfigurationManager import ConfigurationManager
from CsisAPI import CsisAPI
from TOPdeskAPI import TOPdeskAPI
from TimestampUtils import TimestampUtils
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