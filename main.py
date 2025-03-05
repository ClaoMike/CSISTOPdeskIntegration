from CsisAPI import CsisAPI
from TOPdeskAPI import TOPdeskAPI
from TicketConverter import TicketConverter

csisAPI = CsisAPI()
topdeskAPI = TOPdeskAPI()
ticketConverter = TicketConverter()

csisAPI.get_token()

# Check which CSIS tickets do not have a customer reference
# It means they are new
tickets_to_be_created = csisAPI.get_tickets_to_be_created()
# convert the CSIS ticket to TOPdesk ticket
tickets_to_be_created = ticketConverter.convert_tickets_to_TOPdesk_format(tickets_to_be_created)
# Create the ticket in TOPdesk
created_tickets = topdeskAPI.create_tickets(tickets_to_be_created)
# Update the CSIS ticket with a reference to the TOPdesk ticket
csisAPI.update_tickets(created_tickets)

# TODO: log, documentation, test, the rest