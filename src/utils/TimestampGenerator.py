"""
TimestampGenerator Module
-------------------------

This module provides a `TimestampGenerator` class for handling timestamp-related operations, including:
- Generating timestamps relative to the current UTC time.
- Calculating the difference between two timestamps in minutes.

The class is implemented as a Singleton to ensure only one instance exists.

Usage Example:
--------------
    from timestamp_generator import TimestampGenerator

    generator = TimestampGenerator()

    # Get a timestamp for 30 minutes ago
    past_timestamp = generator.get_timestamp(30)
    print(past_timestamp)  # Example Output: "2025-03-10T09:18:59.060Z"

    # Calculate time difference between two timestamps
    t1 = "2025-03-10T09:48:59.060325"
    t2 = "2025-03-10T10:00:00.000000"
    diff_minutes = generator.get_time_difference_between(t1, t2)
    print(diff_minutes)  # Output: 11
"""

import datetime
import math


class TimestampGenerator:
    """
    A Singleton class to generate and manipulate timestamps.

    Attributes:
        _instance (TimestampGenerator): A private class instance for Singleton behavior.

    Methods:
        get_timestamp(minutes: int) -> str:
            Generates a UTC timestamp from the current time minus the specified minutes.

        get_time_difference_between(t1: str, t2: str) -> int:
            Computes the absolute difference between two timestamps in minutes.
    """

    _instance = None  # Singleton instance

    def __new__(cls):
        """
        Ensures that only one instance of the class is created (Singleton pattern).

        Returns:
            TimestampGenerator: The singleton instance of the class.
        """
        if cls._instance is None:
            cls._instance = super(TimestampGenerator, cls).__new__(cls)
            cls._instance.__initialize()
        return cls._instance

    def __initialize(self):
        """
        Initializes the class variables. Ensures initialization happens only once.
        """
        if not hasattr(self, "_initialized"):
            self._initialized = True

    def get_start_of_the_search_timestamp(self, minutes: int) -> str:
        """
        Generates a timestamp representing the current UTC time minus the specified minutes.

        Args:
            minutes (int): The number of minutes to subtract from the current UTC time.

        Returns:
            str: The generated timestamp in ISO 8601 format (trimmed to 3 decimal places).

        Example:
            >>> generator = TimestampGenerator()
            >>> generator.get_start_of_the_search_timestamp(10)
            "2025-03-10T09:38:59.060Z"
        """
        new_time = datetime.datetime.utcnow() - datetime.timedelta(minutes=minutes)
        return new_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"  # Trim to 3 decimal places

    def get_time_difference_between(self, t1: str, t2: str) -> int:
        """
        Calculates the absolute difference in minutes between two ISO 8601 timestamps.

        Args:
            t1 (str): The first timestamp (ISO 8601 format).
            t2 (str): The second timestamp (ISO 8601 format).

        Returns:
            int: The absolute difference between the two timestamps in minutes.

        Example:
            >>> generator = TimestampGenerator()
            >>> generator.get_time_difference_between("2025-03-10T09:48:59.060325", "2025-03-10T10:00:00.000000")
            11
        """
        dt1 = datetime.datetime.fromisoformat(t1)
        dt2 = datetime.datetime.fromisoformat(t2)

        # Compute difference
        diff = dt2 - dt1

        # Convert to minutes (rounded)
        minutes_diff = math.ceil(abs(diff.total_seconds() / 60))

        return minutes_diff
