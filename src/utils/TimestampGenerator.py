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

    def get_time_difference_between(self, t1, t2):
        dt1 = datetime.datetime.fromisoformat(t1)
        dt2 = datetime.datetime.fromisoformat(t2)

        # Compute difference
        diff = dt2 - dt1

        # Convert to minutes
        minutes_diff = round(abs(diff.total_seconds() / 60))

        return minutes_diff
