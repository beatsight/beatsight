import pytz
from datetime import datetime, timezone

def timestamp_to_dt(ts: int, timezone_offset: int):
    timezone = pytz.FixedOffset(timezone_offset // 60)  # Convert minutes to hours
    return datetime.fromtimestamp(ts, tz=timezone)

