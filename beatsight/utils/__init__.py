import json
import datetime as dt
from datetime import datetime
from collections import defaultdict

import pandas
import duckdb

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime) or isinstance(obj, pandas.Timestamp):
            # Format datetimes according to your desired format (e.g., ISO-8601)
            return obj.isoformat()
        return super().default(obj)

def recent_weekly_commit_count(data, past_weeks=52):
    # Get the Monday of the current week
    today = datetime.now(tz=dt.timezone.utc)
    this_monday = (today - dt.timedelta(days=today.weekday())).date()

    # Calculate the start date for the past 52 weeks
    start_date = this_monday - dt.timedelta(weeks=52)

    data_dict = defaultdict(int)
    # Iterate through the data and add the data to the dictionary
    for item in data:
        # week_date = datetime.strptime(item['week'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.utc)
        week_start_date = item['week']
        if start_date <= week_start_date <= this_monday:
            data_dict[item['week']] = item['commit_count']

    past_52_weeks = [this_monday - dt.timedelta(weeks=x) for x in range(past_weeks)]
    filtered_data = [
        {'week': week, 'commit_count': data_dict[week]} for week in past_52_weeks
    ]
    return filtered_data
