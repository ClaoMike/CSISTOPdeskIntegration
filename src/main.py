from src.API.CsisAPI import CsisAPI
from src.API.TOPdeskAPI import TOPdeskAPI
from src.utils.Logger import Logger
from src.utils.TicketConverter import TicketConverter

logger = Logger()

csisAPI = CsisAPI()
topdeskAPI = TOPdeskAPI()
ticketConverter = TicketConverter()

# Get access token #####################################################################################################

# Logging ##############################################################################################################
logger.info_new_section(message="Fetching the CSIS access token")
logger.newline()
# END Logging ##########################################################################################################

csisAPI.get_token()

# Logging ##############################################################################################################
logger.info_end_section(message="DONE Fetching the CSIS access token")
logger.newline()
# END Logging ##########################################################################################################
# END Get access token #################################################################################################

# Create new tickets ###################################################################################################

# Logging ##############################################################################################################
logger.info_new_section(message="Fetching recently created tickets from CSIS")
logger.newline()
# END Logging ##########################################################################################################

# Check which CSIS tickets do not have a customer reference
# It means they are new
tickets_to_be_created = csisAPI.get_tickets_to_be_created()

# Logging ##############################################################################################################
logger.array(tickets_to_be_created, array_title="CSIS Tickets to be created")
logger.info_end_section(message="DONE Fetching recently created tickets from CSIS")
logger.newline()

logger.info_new_section(message="Converting the fetched-recently-created tickets from CSIS to TOPdesk format")
logger.newline()
# END Logging ##########################################################################################################

# convert the CSIS ticket to TOPdesk ticket
tickets_to_be_created = ticketConverter.convert_tickets_to_be_created_to_TOPdesk_format(tickets_to_be_created)

# Logging ##############################################################################################################
logger.array(tickets_to_be_created, array_title="CSIS Tickets to be created (TOPdesk format)")
logger.info_end_section(message="DONE Converting fetched-recently-created tickets from CSIS")
logger.newline()

logger.info_new_section(message="Creating the converted tickets in TOPdesk")
logger.newline()


# Create the ticket in TOPdesk
created_tickets = topdeskAPI.create_tickets(tickets_to_be_created)

# Logging ##############################################################################################################
logger.array(created_tickets, array_title="CSIS Tickets created in TOPdesk")
logger.info_end_section(message="DONE Creating the converted tickets in TOPdesk")
logger.newline()

logger.info_new_section(message="Updating the CSIS tickets with the TOPdesk's IDs")
logger.newline()
# END Logging ##########################################################################################################

# Update the CSIS ticket with a reference to the TOPdesk ticket
csisAPI.update_tickets(created_tickets)

logger.info_end_section(message="DONE Updating the CSIS tickets with the TOPdesk's IDs")
logger.newline()
# END Logging ##########################################################################################################
# END Create new tickets ###############################################################################################

# Update tickets #######################################################################################################

# Logging ##############################################################################################################
logger.info_new_section(message="Fetching the CSIS tickets that have been recently updated")
logger.newline()
# END Logging ##########################################################################################################

tickets_to_be_updated = csisAPI.get_updated_tickets()

# Logging ##############################################################################################################
logger.array(tickets_to_be_updated, array_title="CSIS Tickets recently updated")
logger.info_end_section(message="DONE Fetching the CSIS tickets that have been recently updated")
logger.newline()

logger.info_new_section(message="Converting the fetched recently-created tickets")
logger.newline()
# END Logging ##########################################################################################################

tickets_to_be_updated = ticketConverter.convert_updated_tickets_to_TOPdesk_format(tickets_to_be_updated)

# Logging ##############################################################################################################
logger.array(tickets_to_be_updated, array_title="CSIS Tickets recently updated (TOPdesk format)")
logger.info_end_section(message="DONE Converting the fetched recently-created tickets")
logger.newline()

logger.info_new_section(message="Updating the converted fetched-recently-created tickets")
# END Logging ##########################################################################################################

topdeskAPI.update_tickets(tickets_to_be_updated)

# Logging ##############################################################################################################
logger.newline()
logger.info_end_section(message="DONE Updating the converted fetched-recently-created tickets")
logger.newline()
# END Logging ##########################################################################################################
# END Update tickets ###################################################################################################

# TODO: documentation, test, the rest
