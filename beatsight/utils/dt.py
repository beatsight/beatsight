import pytz
from datetime import datetime, timezone

def timestamp_to_dt(ts: int, timezone_offset:int):
    dt = datetime.fromtimestamp(ts)
    # Convert datetime to timezone-aware object
    timezone = pytz.FixedOffset(timezone_offset // 60)  # Convert minutes to hours
    return dt.replace(tzinfo=timezone)
