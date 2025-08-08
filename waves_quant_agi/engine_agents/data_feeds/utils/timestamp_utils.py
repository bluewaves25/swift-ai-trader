from typing import Optional
from datetime import datetime
import pytz

class TimestampUtils:
    def get_timestamp(self, timezone: str = "UTC") -> float:
        """Generate a timezone-aware timestamp."""
        try:
            tz = pytz.timezone(timezone)
            return datetime.now(tz).timestamp()
        except Exception as e:
            print(f"Error generating timestamp: {e}")
            return datetime.now().timestamp()

    def align_timestamp(self, timestamp: float, interval: int = 1) -> float:
        """Align timestamp to a specific interval (seconds)."""
        try:
            return round(timestamp / interval) * interval
        except Exception as e:
            print(f"Error aligning timestamp: {e}")
            return timestamp