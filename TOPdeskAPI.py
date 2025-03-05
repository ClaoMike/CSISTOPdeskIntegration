import datetime

class TOPdeskAPI:
    _instance = None  # Singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TOPdeskAPI, cls).__new__(cls)
            cls._instance.__initialize()
        return cls._instance

    def __initialize(self):
        """Initialize variables"""
        if not hasattr(self, "_initialized"):
            self._initialized = True

    def create_tickets(self, tickets):
        pass