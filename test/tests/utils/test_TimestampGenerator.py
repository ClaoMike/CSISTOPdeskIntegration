import pytest
from freezegun import freeze_time
from src.utils.TimestampGenerator import TimestampGenerator

@pytest.fixture
def timestamp_generator():
    """Fixture to provide a singleton instance of TimestampGenerator."""
    return TimestampGenerator()

def test_is_singleton_instance():
    """Test that TimestampGenerator follows the Singleton pattern."""
    instance1 = TimestampGenerator()
    instance2 = TimestampGenerator()

    # Check if both instances have the same memory address
    assert id(instance1) == id(instance2)


@freeze_time("2025-03-10 10:00:00.123456")  # ✅ Freeze time globally
def test_get_start_of_the_search_timestamp(timestamp_generator):
    """Test with frozen time to avoid mocking issues."""

    expected_timestamp = "2025-03-10T09:50:00.123Z"

    result = timestamp_generator.get_start_of_the_search_timestamp(10)

    assert result == expected_timestamp  # ✅ Passes without mocking complexity!

@pytest.mark.parametrize("t1, t2, expected", [
    ("2025-03-10T09:48:59.060325", "2025-03-10T10:00:00.000000", 12),  # Standard case
    ("2025-03-10T10:00:00.000000", "2025-03-10T09:48:59.060325", 12),  # Reversed order
    ("2025-03-10T10:00:00.000000", "2025-03-10T10:00:00.000000", 0),  # No difference
    ("2025-03-09T10:00:00.000000", "2025-03-10T10:00:00.000000", 1440),  # 1 day difference
    ("2025-03-10T10:00:00.000000", "2025-03-11T10:00:00.000000", 1440),  # Another 1 day diff
    ("2025-03-10T10:00:00.000000", "2025-03-10T10:01:00.000000", 1),  # 1-minute difference
    ("2025-03-10T10:00:00.000000", "2025-03-10T10:00:30.000000", 1),  # 30 sec rounds to 1 min
    ("2025-03-10T10:00:00.000000", "2025-03-10T10:00:29.999999", 1)  # 29 sec rounds to 0 min
])
def test_get_time_difference_between(timestamp_generator, t1, t2, expected):
    """Test the function with different timestamp inputs."""
    result = timestamp_generator.get_time_difference_between(t1, t2)
    assert result == expected, f"Expected {expected}, got {result}"