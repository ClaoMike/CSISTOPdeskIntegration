# CSIS to TOPdesk synchronization script

**Author**: Claudiu Mihai Jechel

## Description
This script operates in two steps:
1. Ticket Creation & Linking:
   - Retrieve all CSIS tickets created since the last time.
   - Create corresponding tickets in TOPdesk.
   - Update the CSIS tickets with their respective TOPdesk ticket IDs.
2. Ticket Updates:
   - Retrieve all CSIS tickets updated since the last time.
   - Apply the corresponding updates to their linked TOPdesk tickets.

**NOTES**:
- Can be manually run, but also as an Azure Automations script.
