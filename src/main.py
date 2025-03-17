"""
CSIS to TOPdesk Ticket Synchronization Script
---------------------------------------------

This script:
- Fetches and processes tickets from CSIS.
- Converts CSIS tickets to TOPdesk format.
- Creates new tickets in TOPdesk.
- Updates CSIS tickets with TOPdesk references.
- Fetches and updates recently modified CSIS tickets in TOPdesk.

The script follows these steps:
1. **Authenticate with CSIS API** - Retrieves an access token.
2. **Fetch and Create New Tickets** - Identifies new CSIS tickets and creates them in TOPdesk.
3. **Update CSIS with TOPdesk IDs** - Updates CSIS tickets with their corresponding TOPdesk references.
4. **Update Existing Tickets** - Synchronizes changes from CSIS to TOPdesk.

Dependencies:
- `CsisAPI` for interacting with the CSIS API.
- `TOPdeskAPI` for handling TOPdesk API interactions.
- `Logger` for structured logging.
- `TicketConverter` for format conversion.

Usage:
--------------
    Run this script to synchronize CSIS and TOPdesk tickets.

"""

from src.API.CsisAPI import CsisAPI
from src.API.TOPdeskAPI import TOPdeskAPI
from src.config.ConfigurationManager import ConfigurationManager
from src.utils.Logger import Logger
from src.utils.TicketConverter import TicketConverter

# Initialize configuration
config = ConfigurationManager()

# Initialize logger
logger = Logger(is_logging=config.is_logging)

# Initialize API handlers
csisAPI = CsisAPI()
topdeskAPI = TOPdeskAPI()
ticketConverter = TicketConverter()

# ==========================
# STEP 1: Get CSIS Access Token
# ==========================

logger.info_new_section(message="Fetching the CSIS access token")
logger.newline()

csisAPI.get_token()

logger.info_end_section(message="DONE Fetching the CSIS access token")
logger.newline()

# ==========================
# STEP 2: Create New Tickets
# ==========================

logger.info_new_section(message="Fetching recently created tickets from CSIS")
logger.newline()

# Identify new tickets in CSIS (those without a customer reference)
tickets_to_be_created = csisAPI.get_tickets_to_be_created()

logger.array(tickets_to_be_created, array_title="CSIS Tickets to be created")
logger.info_end_section(message="DONE Fetching recently created tickets from CSIS")
logger.newline()

logger.info_new_section(message="Converting the fetched recently-created tickets from CSIS to TOPdesk format")
logger.newline()

# Convert CSIS ticket format to TOPdesk ticket format
tickets_to_be_created = ticketConverter.convert_tickets_to_be_created_to_TOPdesk_format(tickets_to_be_created)

logger.array(tickets_to_be_created, array_title="CSIS Tickets to be created (TOPdesk format)")
logger.info_end_section(message="DONE Converting fetched recently-created tickets from CSIS")
logger.newline()

logger.info_new_section(message="Creating the converted tickets in TOPdesk")
logger.newline()

# Create the tickets in TOPdesk
created_tickets = topdeskAPI.create_tickets(tickets_to_be_created)

logger.array(created_tickets, array_title="CSIS Tickets created in TOPdesk")
logger.info_end_section(message="DONE Creating the converted tickets in TOPdesk")
logger.newline()

logger.info_new_section(message="Updating the CSIS tickets with the TOPdesk's IDs")
logger.newline()

# Update CSIS tickets with the corresponding TOPdesk ticket IDs
csisAPI.update_tickets(created_tickets)

logger.info_end_section(message="DONE Updating the CSIS tickets with the TOPdesk's IDs")
logger.newline()

# ==========================
# STEP 3: Update Existing Tickets
# ==========================

logger.info_new_section(message="Fetching the CSIS tickets that have been recently updated")
logger.newline()

# Fetch CSIS tickets that have been modified recently
tickets_to_be_updated = csisAPI.get_updated_tickets()

logger.array(tickets_to_be_updated, array_title="CSIS Tickets recently updated")
logger.info_end_section(message="DONE Fetching the CSIS tickets that have been recently updated")
logger.newline()

logger.info_new_section(message="Converting the fetched recently updated tickets")
logger.newline()

# Convert CSIS updated tickets to TOPdesk format
tickets_to_be_updated = ticketConverter.convert_updated_tickets_to_TOPdesk_format(tickets_to_be_updated)

logger.dictionary(tickets_to_be_updated, dict_title="CSIS Tickets recently updated (TOPdesk format)")
logger.info_end_section(message="DONE Converting the fetched recently updated tickets")
logger.newline()

logger.info_new_section(message="Updating the converted fetched-recently-updated tickets")

# Push updates to TOPdesk
topdeskAPI.update_tickets(tickets_to_be_updated)

logger.newline()
logger.info_end_section(message="DONE Updating the converted fetched-recently-updated tickets")
logger.newline()

# ==========================
# END OF PROCESS
# ==========================

logger.info("Synchronization process completed successfully.")
logger.close()

# TODO: v1
# fix all warnings and typos
# visualization diagram
# write README
# generate documentation
# set up Azure Credentials
# set up Azure Automations
# release

# TODO: v2
# set up folder for storing logs
# send logs via API
# release