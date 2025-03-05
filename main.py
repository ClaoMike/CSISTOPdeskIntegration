import datetime
from ConfigurationManager import ConfigurationManager
from CsisAPI import CsisAPI

configurationManager = ConfigurationManager()
csisAPI = CsisAPI()

csisAPI.get_token()
tickets_to_be_created = csisAPI.get_tickets_created_after("2024-10-27T09:00:17.242Z")

for ticket in tickets_to_be_created:
    print(ticket)
print(len(tickets_to_be_created))