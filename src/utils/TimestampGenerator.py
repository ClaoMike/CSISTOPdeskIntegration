import datetime

class TimestampGenerator:
    _instance = None  # Singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TimestampGenerator, cls).__new__(cls)
            cls._instance.__initialize()
        return cls._instance

    def __initialize(self):
        """Initialize variables"""
        if not hasattr(self, "_initialized"):
            self._initialized = True

    def get_timestamp(self, minutes: int) -> str:
        """Generate a timestamp for current time minus given minutes."""
        # TODO: is time behind with 1 hour?
        new_time = datetime.datetime.utcnow() - datetime.timedelta(minutes=minutes)
        return new_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"  # Trim to 3 decimal places
