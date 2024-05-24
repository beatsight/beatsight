from datetime import datetime
import json

import pandas
import duckdb

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime) or isinstance(obj, pandas.Timestamp):
            # Format datetimes according to your desired format (e.g., ISO-8601)
            return obj.isoformat()
        return super().default(obj)
