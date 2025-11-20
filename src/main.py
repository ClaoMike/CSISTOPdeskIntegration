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
from src.utils.TicketConverter import TicketConverter
from datetime import datetime

# Initialize configuration
print("Initialize configuration")
config = ConfigurationManager()
print("DONE Initialize configuration")

# Initialize API handlers
csisAPI = CsisAPI()
topdeskAPI = TOPdeskAPI()
ticketConverter = TicketConverter()

# ==========================
# STEP 1: Get CSIS Access Token
# ==========================

print("Fetching the CSIS access token")

csisAPI.get_token()

print("DONE Fetching the CSIS access token")

# ==========================
# STEP 2: Create New Tickets
# ==========================

print("Fetching recently created tickets from CSIS")

# Identify new tickets in CSIS (those without a customer reference)
tickets_to_be_created = csisAPI.get_tickets_to_be_created()

now = datetime.utcnow().replace(tzinfo=timezone.utc)
now_as_azure_string = datetime_to_ms_timestamp(now)
automationassets.set_automation_variable("CSIS_LAST_NEW_TICKETS_TIMESTAMP", now_as_azure_string)
print(f"New tickets timestamp: {now}")

print("CSIS Tickets to be created")
print(tickets_to_be_created)
print("DONE Fetching recently created tickets from CSIS")

print("Converting the fetched recently-created tickets from CSIS to TOPdesk format")

# Convert CSIS ticket format to TOPdesk ticket format
tickets_to_be_created = ticketConverter.convert_tickets_to_be_created_to_TOPdesk_format(tickets_to_be_created)

print("CSIS Tickets to be created (TOPdesk format)")
print(tickets_to_be_created)
print("DONE Converting fetched recently-created tickets from CSIS")

print("Creating the converted tickets in TOPdesk")

# Create the tickets in TOPdesk
created_tickets = topdeskAPI.create_tickets(tickets_to_be_created)

print("CSIS Tickets created in TOPdesk")
print(created_tickets)
print("DONE Creating the converted tickets in TOPdesk")

print("Updating the CSIS tickets with the TOPdesk's IDs")

# Update CSIS tickets with the corresponding TOPdesk ticket IDs
csisAPI.update_tickets(created_tickets)

print("DONE Updating the CSIS tickets with the TOPdesk's IDs")

# ==========================
# STEP 3: Update Existing Tickets
# ==========================

print("Fetching the CSIS tickets that have been recently updated")

# Fetch CSIS tickets that have been modified recently
tickets_to_be_updated = csisAPI.get_updated_tickets()

now = datetime.utcnow().replace(tzinfo=timezone.utc)
now_as_azure_string = datetime_to_ms_timestamp(now)
automationassets.set_automation_variable("CSIS_LAST_UPDATES_TIMESTAMP", now_as_azure_string)
print(f"Updates timestamp: {now}")

print("CSIS Tickets recently updated")
print(tickets_to_be_updated)
print("DONE Fetching the CSIS tickets that have been recently updated")

print("Converting the fetched recently updated tickets")

# Convert CSIS updated tickets to TOPdesk format
tickets_to_be_updated = ticketConverter.convert_updated_tickets_to_TOPdesk_format(tickets_to_be_updated)

print("CSIS Tickets recently updated (TOPdesk format)")
print(tickets_to_be_updated)
print("DONE Converting the fetched recently updated tickets")

print("Updating the converted fetched-recently-updated tickets")

# Push updates to TOPdesk
topdeskAPI.update_tickets(tickets_to_be_updated)

print("DONE Updating the converted fetched-recently-updated tickets")

# ==========================
# END OF PROCESS
# ==========================

print("Synchronization process completed successfully.")