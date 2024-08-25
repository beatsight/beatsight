'''
run as:

root@775e516e09b8:/Users/xiez/dev/beatsight# export DJANGO_SETTINGS_MODULE=beatsight.settings
root@775e516e09b8:/Users/xiez/dev/beatsight# python3 scripts/duckdb-migrations/populate_corrected_fields.py

'''

import os

import duckdb

import django
django.setup()

from django.conf import settings

from projects.models import Project

def update_all():
    for p in Project.objects.all():
        db = os.path.join(settings.STAT_DB_DIR, f"{p.name}_log")
        try:
            update_one(db)
        except Exception as e:
            print(e)

    print('Done')

def update_one(db):
    with duckdb.connect(db) as con:
        con.execute(
            """
                ALTER TABLE gitlog ADD COLUMN corrected_insertions INTEGER;
                """
        )
        con.execute(
            """
                ALTER TABLE gitlog ADD COLUMN corrected_deletions INTEGER;
                """
        )

update_all()
