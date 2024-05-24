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


def save_dataframe_to_duckdb(df, table_name, if_exists='replace'):
    with duckdb.connect("stats.duckdb") as conn:
        df.to_sql(table_name, conn, if_exists=if_exists, index=False)

def delete_dataframes_from_duckdb(table_name, clause):
    with duckdb.connect("stats.duckdb") as conn:
        conn.execute(f"delete from {table_name} where {clause}")
