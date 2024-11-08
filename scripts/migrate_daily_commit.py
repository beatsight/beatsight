import os
import sys

import duckdb

# Directory name to create
base_dir = '/data/stats'
dir_name = f'{base_dir}/daily_commits.parq'
daily_commits = f'{base_dir}/daily_commits'

if os.path.exists(dir_name):
    print(f"The directory '{dir_name}' exists. Quit.")
    sys.exit(0)

print(f"The directory '{dir_name}' does not exist. Start migrating...")

# Function to find all files ending with '_log'
def find_log_files(directory):
    log_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('_log'):
                log_files.append(os.path.join(root, file))
    return log_files

proj_names = []
for fn in find_log_files(base_dir):
    proj_name = fn.split('/')[-1].split('_')[0]
    proj_names.append(proj_name)

os.mkdir(dir_name)

def create_parquet(proj_name):
    with duckdb.connect(daily_commits) as con:
        con.sql(
            f"COPY (select * from author_daily_commits where project = '{proj_name}') TO '{dir_name}/{proj_name}.parquet' (FORMAT 'parquet');"
        )

for proj_name in proj_names:
    create_parquet(proj_name)

# mv daily_commits daily_commits.bak
os.rename(daily_commits, f"{daily_commits}.bak")

def create_view():
    with duckdb.connect(daily_commits) as con:
        con.sql(
            f"CREATE VIEW author_daily_commits AS SELECT * FROM read_parquet('{dir_name}/*.parquet', union_by_name = true);"
        )

create_view()

print('Done.')
