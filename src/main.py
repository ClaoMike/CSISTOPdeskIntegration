from src.API.CsisAPI import CsisAPI
from src.API.TOPdeskAPI import TOPdeskAPI
from src.utils.Logger import Logger
from src.utils.TicketConverter import TicketConverter

logger = Logger()

csisAPI = CsisAPI()
topdeskAPI = TOPdeskAPI()
ticketConverter = TicketConverter()

# Get access token #####################################################################################################
logger.info_new_section(message="Fetching the CSIS access token")
csisAPI.get_token()
logger.info_end_section(message="DONE Fetching the CSIS access token")
########################################################################################################################

# Create new tickets ###################################################################################################
# Check which CSIS tickets do not have a customer reference
# It means they are new
logger.info_new_section(message="Fetching recently created tickets from CSIS")
tickets_to_be_created = csisAPI.get_tickets_to_be_created()
logger.array(tickets_to_be_created, array_title="CSIS Tickets to be created")
logger.info_end_section(message="DONE Fetching recently created tickets from CSIS")

# convert the CSIS ticket to TOPdesk ticket
logger.info_new_section(message="Converting the fetched-recently-created tickets from CSIS to TOPdesk format")
tickets_to_be_created = ticketConverter.convert_tickets_to_be_created_to_TOPdesk_format(tickets_to_be_created)
logger.array(tickets_to_be_created, array_title="CSIS Tickets to be created (TOPdesk format)")
logger.info_end_section(message="DONE Converting fetched-recently-created tickets from CSIS")


# Create the ticket in TOPdesk
logger.info_new_section(message="Creating the converted tickets in TOPdesk")
created_tickets = topdeskAPI.create_tickets(tickets_to_be_created)
logger.array(created_tickets, array_title="CSIS Tickets created in TOPdesk")
logger.info_end_section(message="DONE Creating the converted tickets in TOPdesk")

# Update the CSIS ticket with a reference to the TOPdesk ticket
logger.info_new_section(message="Updating the CSIS tickets with the TOPdesk's IDs")
csisAPI.update_tickets(created_tickets)
# logger.array(, array_title="CSIS Tickets updated with TOPdesk IDs") TODO: Update this
logger.info_end_section(message="DONE Updating the CSIS tickets with the TOPdesk's IDs")
########################################################################################################################

# Update tickets #######################################################################################################
logger.info_new_section(message="Fetching the CSIS tickets that have been recently updated")
tickets_to_be_updated = csisAPI.get_updated_tickets()
logger.array(tickets_to_be_updated, array_title="CSIS Tickets recently updated")
logger.info_end_section(message="DONE Fetching the CSIS tickets that have been recently updated")

logger.info_new_section(message="Converting the fetched recently-created tickets")
tickets_to_be_updated = ticketConverter.convert_updated_tickets_to_TOPdesk_format(tickets_to_be_updated)
logger.array(tickets_to_be_updated, array_title="CSIS Tickets recently updated (TOPdesk format)")
logger.info_end_section(message="DONE Converting the fetched recently-created tickets")

logger.info_new_section(message="Updating the converted fetched-recently-created tickets")
topdeskAPI.update_tickets(tickets_to_be_updated)
# logger.array(tickets_to_be_updated, array_title="CSIS Tickets recently updated (TOPdesk format)") TODO: Update this
logger.info_end_section(message="DONE Updating the converted fetched-recently-created tickets")
########################################################################################################################

# TODO: log, documentation, test, the rest
