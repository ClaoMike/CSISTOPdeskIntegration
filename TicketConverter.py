import requests
from ConfigurationManager import ConfigurationManager


class TicketConverter:
    _instance = None  # Singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TicketConverter, cls).__new__(cls)
            cls._instance.__initialize()
        return cls._instance

    def __initialize(self):
        """Initialize variables"""
        if not hasattr(self, "_initialized"):
            self._initialized = True

    def convert_tickets_to_TOPdesk_format(self, tickets):
        return tickets
