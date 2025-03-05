from CsisAPI import CsisAPI
from TOPdeskAPI import TOPdeskAPI
from TicketConverter import TicketConverter

csisAPI = CsisAPI()
topdeskAPI = TOPdeskAPI()
ticketConverter = TicketConverter()

csisAPI.get_token()

tickets_to_be_created = csisAPI.get_tickets_to_be_created()
tickets_to_be_created = ticketConverter.convert_tickets_to_TOPdesk_format(tickets_to_be_created)
topdeskAPI.create_tickets(tickets_to_be_created)