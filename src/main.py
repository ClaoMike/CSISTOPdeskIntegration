# from src.API.CsisAPI import CsisAPI
# from src.API.TOPdeskAPI import TOPdeskAPI
# from src.utils.TicketConverter import TicketConverter
# from datetime import datetime
from ConfigurationManager import ConfigurationManager

# Initialize configuration
config = ConfigurationManager()

# # Initialize API handlers
# csisAPI = CsisAPI()
# topdeskAPI = TOPdeskAPI()
# ticketConverter = TicketConverter()
#
# # ==========================
# # STEP 1: Get CSIS Access Token
# # ==========================
#
# csisAPI.get_token()
#
# # ==========================
# # STEP 2: Create New Tickets
# # ==========================
#
# # Identify new tickets in CSIS (those without a customer reference)
# tickets_to_be_created = csisAPI.get_tickets_to_be_created()
#
# now = datetime.utcnow().replace(tzinfo=timezone.utc)
# now_as_azure_string = datetime_to_ms_timestamp(now)
# automationassets.set_automation_variable("CSIS_LAST_NEW_TICKETS_TIMESTAMP", now_as_azure_string)
#
# # Convert CSIS ticket format to TOPdesk ticket format
# tickets_to_be_created = ticketConverter.convert_tickets_to_be_created_to_TOPdesk_format(tickets_to_be_created)
#
# # Create the tickets in TOPdesk
# created_tickets = topdeskAPI.create_tickets(tickets_to_be_created)
#
# # Update CSIS tickets with the corresponding TOPdesk ticket IDs
# csisAPI.update_tickets(created_tickets)
#
# # ==========================
# # STEP 3: Update Existing Tickets
# # ==========================
#
# # Fetch CSIS tickets that have been modified recently
# tickets_to_be_updated = csisAPI.get_updated_tickets()
#
# now = datetime.utcnow().replace(tzinfo=timezone.utc)
# now_as_azure_string = datetime_to_ms_timestamp(now)
# automationassets.set_automation_variable("CSIS_LAST_UPDATES_TIMESTAMP", now_as_azure_string)
#
# # Convert CSIS updated tickets to TOPdesk format
# tickets_to_be_updated = ticketConverter.convert_updated_tickets_to_TOPdesk_format(tickets_to_be_updated)
#
# # Push updates to TOPdesk
# topdeskAPI.update_tickets(tickets_to_be_updated)
#
# # ==========================
# # END OF PROCESS
# # ==========================