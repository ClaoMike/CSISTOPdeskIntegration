import datetime
import math
from datetime import datetime, timedelta, timezone
import re
import automationassets

class TimestampUtils:
    @staticmethod
    def get_start_of_the_search_timestamp(minutes: int) -> str:
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
        new_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        return new_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"  # Trim to 3 decimal places

    @staticmethod
    def convert_csis_time_to_UTC_z(date):
        dt = datetime.fromisoformat(date)
        dt_utc = dt.astimezone(timezone.utc)

        return dt_utc.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    @staticmethod
    def get_time_difference_between(t1: str, t2: str) -> int:
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
        t1 = t1.replace("Z", "+00:00")
        t2 = t2.replace("Z", "+00:00")

        dt1 = datetime.fromisoformat(t1)
        dt2 = datetime.fromisoformat(t2)

        # Compute difference
        diff = dt2 - dt1

        # Convert to minutes (rounded)
        minutes_diff = math.ceil(abs(diff.total_seconds() / 60))

        return minutes_diff

    @staticmethod
    def parse_ms_timestamp(ms_timestamp):
        match = re.search(r'/Date\((\d+)\)/', ms_timestamp)
        if match:
            millis = int(match.group(1))
            return datetime.fromtimestamp(millis / 1000.0, tz=timezone.utc)
        else:
            return None

    @staticmethod
    def convert_UTC_z_to_ISO8601(d):
        return datetime.fromisoformat(d.replace("Z", "+00:00"))

    @staticmethod
    def format_to_iso_z(dt):
        if dt is None:
            return None
        return dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'  # Truncate microseconds to milliseconds

    @staticmethod
    def datetime_to_ms_timestamp(dt):
        """Convert datetime (UTC) to milliseconds since epoch, in Azure's /Date(...) format"""
        epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
        millis = int((dt - epoch).total_seconds() * 1000)
        return f"/Date({millis})/"

    @staticmethod
    def parse_Azure_Date_to_iso(date):
        return TimestampUtils.format_to_iso_z(TimestampUtils.parse_ms_timestamp(date))

    @staticmethod
    def save_current_date_as(key: str):
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        now_as_azure_string = TimestampUtils.datetime_to_ms_timestamp(now)
        automationassets.set_automation_variable(key, now_as_azure_string)