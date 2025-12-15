import datetime
from datetime import datetime, timedelta, timezone
import re
import automationassets

class TimestampUtils:
    @staticmethod
    def get_start_of_the_search_timestamp(minutes: int) -> str:
        """Generates a timestamp representing the current UTC time minus the specified minutes."""
        new_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        return new_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"  # Trim to 3 decimal places

    @staticmethod
    def convert_csis_time_to_UTC_z(date):
        dt = datetime.fromisoformat(date)
        dt_utc = dt.astimezone(timezone.utc)

        return dt_utc.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

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
        print(f"Saving {key} ...")
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        print(f"Current time: {now}")
        now -= timedelta(hours=2)
        print(f"Updating to CSIS time: {now}")
        now_as_azure_string = TimestampUtils.datetime_to_ms_timestamp(now)
        automationassets.set_automation_variable(key, now_as_azure_string)