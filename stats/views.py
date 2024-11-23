import os
import json
import sys
import datetime as dt
from datetime import datetime
from collections import defaultdict
from functools import reduce
import logging

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.utils.timezone import get_current_timezone
import pandas as pd
import duckdb
import pygit2
import fastparquet

from beatsight.utils.pl_ext import PL_EXT
from beatsight.utils.dt import timestamp_to_dt
from projects.models import Project, Language, ProjectLanguage, ProjectActivity
from developers.models import (
    Developer, DeveloperLanguage, DeveloperContribution, DeveloperContributionSerializer,
    DeveloperActivity
)
from stats.models import (
    # GeneralData, GeneralDataSerializer,
    ActivityData, ActivityDataSerializer,
    # AuthorData, AuthorDataSerializer,
    # FileData, FileDataSerializer,
)
from vendor.repostat.analysis.gitrepository import GitRepository

from .utils import save_dataframe_to_duckdb, delete_dataframes_from_duckdb, fetch_from_duckdb
from .gitdata import gen_commit_record

logger = logging.getLogger('tasks')

def get_a_project_stat(p: Project, force=False):
    """Get stat data of a project."""
    replace = force

    # get whole/partial repo history
    db = os.path.join(settings.STAT_DB_DIR, f"{p.name}_log")
    whole_history_df = gen_whole_history_df(p, db, replace=replace)
    repo = GitRepository(p.repo_path, whole_history_df=whole_history_df)

    # save current commit as last stat commit
    p.refresh_from_db()
    p.last_stat_commit = p.head_commit
    p.save()

    ### general data
    p.files_count = repo.head.files_count
    ext_df = repo.head.files_extensions_summary
    lang_cnt = defaultdict(int)
    for index, row in ext_df[~ext_df['is_binary']].iterrows():
        extension = row['extension']
        if extension not in PL_EXT:
            continue
        lines_count = row['lines_count']
        lang_cnt[PL_EXT[extension]] += lines_count

    for lang, cnt in lang_cnt.items():
        try:
            lang_obj = Language.objects.get(name=lang)
        except Language.DoesNotExist:
            lang_obj = Language(name=lang)
            lang_obj.save()

        try:
            proj_lang = ProjectLanguage.objects.get(project=p, language=lang_obj)
        except ProjectLanguage.DoesNotExist:
            proj_lang = ProjectLanguage(project=p, language=lang_obj)
        proj_lang.lines_count = cnt
        proj_lang.save()

    sql = f''' SELECT
    commit_sha,
    author_timestamp
    FROM
    gitlog
    ORDER BY
    author_timestamp ASC
    LIMIT 1;
    '''
    res = fetch_from_duckdb(sql, db)
    assert len(res) == 1
    p.first_commit_id, p.first_commit_at = res[0][0], timezone.make_aware(datetime.fromtimestamp(res[0][1]))

    sql = f''' SELECT
    commit_sha,
    author_timestamp
    FROM
    gitlog
    ORDER BY
    author_timestamp DESC
    LIMIT 1;
    '''
    res = fetch_from_duckdb(sql, db)
    assert len(res) == 1
    p.last_commit_id, p.last_commit_at = res[0][0], timezone.make_aware(datetime.fromtimestamp(res[0][1]))
    p.age = (p.last_commit_at - p.first_commit_at).days + 1

    sql = f''' SELECT
    COUNT(*) AS total_commits,
    COUNT(DISTINCT DATE_TRUNC('day', TO_TIMESTAMP(author_timestamp))) AS active_days_count
    FROM
    gitlog
    '''
    res = fetch_from_duckdb(sql, db)
    assert len(res) == 1
    p.commits_count, p.active_days = res[0]
    p.save()
    p.refresh_from_db()

    ### activity stata (past year activity, month_in_year/weekday/hourly activiy )
    # activity_data = data['activity']
    try:
        ac = ActivityData.objects.get(project=p)
    except ActivityData.DoesNotExist:
        ac = ActivityData(project=p)

    sql = f'''SELECT
    DATE_TRUNC('week', TO_TIMESTAMP(author_timestamp)) AS week,
    COUNT(commit_sha) AS commit_count
    FROM gitlog
    GROUP BY week
    ORDER BY week;
    '''
    weekly_activity = []
    for e in fetch_from_duckdb(sql, db):
        weekly_activity.append({
            'week': e[0],
            'commit_count': e[1],
        })
    ac.weekly_activity = weekly_activity

    sql = f'''SELECT
    DATE_TRUNC('month', TO_TIMESTAMP(author_timestamp)) AS month,
    COUNT(commit_sha) AS commit_count
    FROM gitlog
    GROUP BY month
    ORDER BY month;
    '''
    monthly_activity = []
    for e in fetch_from_duckdb(sql, db):
        monthly_activity.append({
            'month': e[0],
            'commit_count': e[1],
        })
    ac.monthly_activity = monthly_activity

    sql = f'''SELECT
    DATE_TRUNC('year', TO_TIMESTAMP(author_timestamp)) AS year,
    COUNT(commit_sha) AS commit_count
    FROM gitlog
    GROUP BY year
    ORDER BY year;
    '''
    yearly_activity = []
    for e in fetch_from_duckdb(sql, db):
        yearly_activity.append({
            'year': e[0],
            'commit_count': e[1],
        })
    ac.yearly_activity = yearly_activity
    ac.save()

    ### authors stat (insertions, deletions, commits_count, active_days_count ...)
    # author_data = data['authors']

    # sql = f'''
    # SELECT author_email,
    # FIRST(author_name) AS author_name,
    # COUNT(*) AS commit_count,
    # SUM(insertions) AS total_insertions,
    # SUM(deletions) AS total_deletions,
    # CAST(TO_TIMESTAMP(min(author_timestamp)) AS DATETIME) AS first_commit_datetime,
    # CAST(TO_TIMESTAMP(max(author_timestamp)) AS DATETIME) AS lastest_commit_datetime,
    # COUNT(DISTINCT DATE_TRUNC('day', TO_TIMESTAMP(author_timestamp))) AS active_days_count
    # FROM {p.name}
    # GROUP BY author_email
    # ORDER BY commit_count DESC;
    # '''

    sql = f'''
    SELECT author_email,
    FIRST(author_name) AS author_name,
    CAST(TO_TIMESTAMP(min(author_timestamp)) AS DATETIME) AS first_commit_datetime,
    CAST(TO_TIMESTAMP(max(author_timestamp)) AS DATETIME) AS lastest_commit_datetime,
    FROM gitlog
    GROUP BY author_email;
    '''
    for e in fetch_from_duckdb(sql, db):
        # try:
        #     au = AuthorData.objects.get(project=p, author_email=e[0])
        # except AuthorData.DoesNotExist:
        #     au = AuthorData(project=p, author_email=e[0])

        # au.author_email, au.author_name, au.commit_count, au.total_insertions, au.total_deletions = e[0], e[1], e[2], e[3], e[4]
        # au.first_commit_date, au.last_commit_date = timezone.make_aware(e[5]), timezone.make_aware(e[6])
        # au.contributed_days = (au.last_commit_date - au.first_commit_date).days + 1
        # au.active_days = e[7]
        # au.save()

        try:
            dev = Developer.objects.get(email=e[0])
        except Developer.DoesNotExist:
            dev = Developer(email=e[0])
        dev.name = e[1]
        dev.set_first_last_commit_at(timezone.make_aware(e[2]), timezone.make_aware(e[3]))
        # dev.total_commits = au.commit_count
        # dev.total_insertions = au.total_insertions
        # dev.total_deletions = au.total_deletions
        # dev.active_days = au.active_days
        dev.save()
        dev.add_a_project(p)

    # save user daily commits count df
    # should be calculated in local timezones
    df = repo.whole_history_df
    df['author_date'] = pd.to_datetime(df['author_timestamp'], unit='s', utc=True) + pd.to_timedelta(df['author_tz_offset'], unit='m')

    df['author_date'] = df['author_date'].dt.date

    # Group by author_email and date, then calculate the sum of insertions and deletions
    daily_stats = df.groupby(['author_email', 'author_date']).agg({
        'insertions': 'sum',
        'deletions': 'sum',
        'commit_sha': 'count',
        'file_exts': lambda x: list({y for lst in x for y in lst})

    }).reset_index()
    daily_stats.columns = ['author_email', 'author_date', 'insertions', 'deletions', 'daily_commit_count', 'file_exts']
    daily_stats = daily_stats[daily_stats['daily_commit_count'] > 0]

    daily_stats['insertions'] = daily_stats['insertions'].astype('int32')
    daily_stats['deletions'] = daily_stats['deletions'].astype('int32')
    daily_stats['daily_commit_count'] = daily_stats['daily_commit_count'].astype('int32')
    daily_stats['project'] = p.name

    save_daily_commits_parq(daily_stats, p, replace=replace)
    create_daily_commits_view()

    daily_commits_db = os.path.join(settings.STAT_DB_DIR, "daily_commits")

    # calculate authors' activities, most used languages, contributions
    emails  = daily_stats['author_email'].unique().tolist()
    calculate_authors_data(emails, daily_commits_db, p)

# def create_author_daily_commits_table(db):
#     with duckdb.connect(db) as con:
#         table_exists = con.execute(
#             "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'author_daily_commits'"
#         ).fetchone()[0] > 0
#         if not table_exists:
#             con.execute(
#                 """
#                 CREATE TABLE author_daily_commits (
#                 author_email VARCHAR,
#                 author_date DATE,
#                 insertions INT32,
#                 deletions INT32,
#                 daily_commit_count INT32,
#                 file_exts VARCHAR[],
#                 project VARCHAR
#                 );
#                 """
#             )

def save_daily_commits_parq(df, proj, replace=False):
    parq_dir = os.path.join(settings.STAT_DB_DIR, "daily_commits.parq")
    if not os.path.exists(parq_dir):
        os.makedirs(parq_dir)

    parq = os.path.join(parq_dir, f"{proj.name}.parquet")

    if replace:
        try:
            os.remove(parq)
        except FileNotFoundError:
            ...

    with duckdb.connect() as con:
        con.sql(f"COPY (select * from df) TO '{parq}' (FORMAT 'parquet')")
    # else:
    #     # Read existing data from the Parquet file
    #     with duckdb.connect() as con:
    #         existing_df = con.execute(f"SELECT * FROM '{parq}'").fetchdf()
    #         print('existing_df')
    #         print(existing_df)
    #         existing_df['author_date'] = existing_df['author_date'].dt.date

    #         # Append the new data to the existing DataFrame
    #         combined_df = pd.concat([df, existing_df], ignore_index=True)
    #         print('combined_df')
    #         print(combined_df)

    #         # Write the combined DataFrame back to the Parquet file
    #         con.sql(f"COPY (SELECT * FROM combined_df) TO '{parq}' (FORMAT 'parquet')")

def create_daily_commits_view():
    db = os.path.join(settings.STAT_DB_DIR, "daily_commits")
    if os.path.exists(db):
        return

    parqs = os.path.join(settings.STAT_DB_DIR, "daily_commits.parq", "*.parquet")
    with duckdb.connect(db) as con:
        sql = f"CREATE VIEW author_daily_commits AS SELECT * FROM read_parquet('{parqs}', union_by_name = true)"
        con.sql(sql)

def gen_whole_history_df(p, db, replace=False):
    repo = pygit2.Repository(p.repo_path)

    if replace:
        try:
            os.remove(db)
        except FileNotFoundError:
            ...
        ProjectActivity.objects.filter(project=p).delete()

    with duckdb.connect(db) as con:
        table_exists = con.execute(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'gitlog'"
        ).fetchone()[0] > 0
        if not table_exists:
            con.execute(
                "CREATE SEQUENCE gitlog_seq_id START 1"
            )
            con.execute(
                """
                CREATE TABLE gitlog (
                  id INTEGER PRIMARY KEY DEFAULT NEXTVAL('gitlog_seq_id'),
                  commit_sha VARCHAR,
                  is_merge_commit BOOLEAN,
                  author_name TEXT,
                  author_email TEXT,
                  author_tz_offset INTEGER,
                  author_timestamp INTEGER,
                  author_datetime INTEGER,
                  insertions INTEGER,
                  deletions INTEGER,
                  corrected_insertions INTEGER,
                  corrected_deletions INTEGER,
                  file_exts VARCHAR[]
                )
                """
            )

    last_seen_commit = None
    with duckdb.connect(db) as con:
        commit_sha_df = con.sql("SELECT commit_sha FROM gitlog").df()
        if not commit_sha_df.empty:
            last_seen_commit = commit_sha_df['commit_sha'].iloc[-1]

    if last_seen_commit and not replace:
        last_seen_commit_obj = repo.get(last_seen_commit)
    else:
        last_seen_commit_obj = None

    # Retrieve the Git log incrementally
    new_commit_hashes = []
    for commit in repo.walk(repo.head.target, pygit2.GIT_SORT_TOPOLOGICAL):
        if last_seen_commit_obj and commit.id == last_seen_commit_obj.id:
            break
        new_commit_hashes.append(str(commit.id))

    if new_commit_hashes:
        records = []
        activities = []
        for cid in new_commit_hashes[::-1]:
            commit = repo.get(cid)
            e = gen_commit_record(repo, commit, p.get_ignore_list())
            if not e['is_merge_commit']:
                author_datetime = timestamp_to_dt(e['author_timestamp'], e['author_tz_offset'])
                activities.append(ProjectActivity(
                    project=p,
                    commit_sha=e['commit_sha'],
                    commit_message=e['commit_msg'].strip(),
                    author_name=e['author_name'],
                    author_email=e['author_email'],
                    author_datetime=author_datetime,
                    details=e['details'],
                    insertions=e['insertions'],
                    deletions=e['deletions'],
                    corrected_insertions=e['corrected_insertions'],
                    corrected_deletions=e['corrected_deletions'],
                ))

            del e['commit_msg']
            del e['details']
            records.append(e)

        ProjectActivity.objects.bulk_create(activities, batch_size=999, ignore_conflicts=True)

        df = pd.DataFrame(records)
        df['author_name'] = pd.Categorical(df['author_name'])
        df['author_email'] = pd.Categorical(df['author_email'])
        with duckdb.connect(db) as con:
            con.execute(
                """INSERT INTO gitlog (
                commit_sha, is_merge_commit, author_name, author_email, author_tz_offset, author_timestamp,
                author_datetime, insertions, deletions, corrected_insertions, corrected_deletions, file_exts
                ) SELECT * FROM df"""
            )

    with duckdb.connect(db) as con:
        df = con.sql("SELECT * FROM 'gitlog'").df()
        assert not df.empty, f"gitlog is empty {db}"
        return df

## user related
def calculate_authors_data(emails, daily_commits_db, proj=None):
    for email in emails:
        try:
            dev = Developer.objects.get(email=email)
        except Developer.DoesNotExist:
            # raise warning
            continue

        populate_general_data(dev, db=daily_commits_db)

        try:
            dev_ac = DeveloperActivity.objects.get(developer=dev)
        except DeveloperActivity.DoesNotExist:
            dev_ac = DeveloperActivity(developer=dev)

        dev_ac.daily_activity = get_author_daily_commit_count(email, db=daily_commits_db)
        dev_ac.weekly_activity = get_author_weekly_commit_count(email, db=daily_commits_db)
        dev_ac.save()

        for lang, cnt in get_most_used_langs(email, db=daily_commits_db):
            try:
                lang_obj = Language.objects.get(name=lang)
            except Language.DoesNotExist:
                lang_obj = Language(name=lang)
                lang_obj.save()

            try:
                dev_lang = DeveloperLanguage.objects.get(developer=dev, language=lang_obj)
            except DeveloperLanguage.DoesNotExist:
                dev_lang = DeveloperLanguage(developer=dev, language=lang_obj)
            dev_lang.use_count = cnt
            dev_lang.save()

        if proj is not None:
            try:
                dev_contrib = DeveloperContribution.objects.get(developer=dev, project=proj)
            except DeveloperContribution.DoesNotExist:
                dev_contrib = DeveloperContribution(developer=dev, project=proj)
            dev_contrib.daily_contribution = get_author_daily_contributions(
                email, proj, db=daily_commits_db
            )
            dev_contrib.commits_count = sum(e['daily_commit_count'] for e in dev_contrib.daily_contribution)
            dev_contrib.save()

def populate_general_data(dev, db):
    sql = f"""
SELECT
    MIN(author_date) AS earliest_author_date,
    MAX(author_date) AS latest_author_date,
    SUM(daily_commit_count) AS total_commit_count,
    SUM(insertions) AS total_insertions,
    SUM(deletions) AS total_deletions,
    COUNT(DISTINCT author_date) AS distinct_author_date_count
FROM
    author_daily_commits
WHERE
    author_email = '{dev.email}';
    """
    for e in fetch_from_duckdb(sql, db=db):
        dev.total_commits = e[2] or 0
        dev.total_insertions = e[3] or 0
        dev.total_deletions = e[4] or 0
        dev.active_days = e[5] or 0
        dev.save()
    dev.calculate_rank()

def get_most_used_langs(email, db):
    sql = f"""
    select file_exts from author_daily_commits where author_email = '{email}'
    """
    file_exts_df = fetch_from_duckdb(sql, to_df=True, db=db)

    tmp = pd.DataFrame([x for row in file_exts_df['file_exts'] for x in row], columns=['file_ext'])
    top_file_exts = tmp.groupby('file_ext').size().sort_values(ascending=False).head(10)
    lang_cnt = defaultdict(int)
    for fe, count in top_file_exts.items():
        if fe not in PL_EXT:
            continue
        lang_cnt[PL_EXT[fe]] += count
    return lang_cnt.items()

def get_author_weekly_commit_count(email, db):
    sql = f'''
SELECT
    DATE_TRUNC('week', author_date) AS week_start_date,
    SUM(daily_commit_count) AS weekly_commit_count_sum
FROM
    author_daily_commits
WHERE
    author_email = '{email}'
GROUP BY
    week_start_date
ORDER BY
    week_start_date
    '''
    weekly_commit_count = []
    for e in fetch_from_duckdb(sql, db):
        weekly_commit_count.append({
            'week': e[0],
            'commit_count': e[1],
        })

    return weekly_commit_count

def get_author_daily_commit_count(email, db):
    sql = f'''
SELECT
    author_date,
    SUM(daily_commit_count) AS weekly_commit_count_sum
FROM
    author_daily_commits
WHERE
    author_email = '{email}'
GROUP BY
    author_date
ORDER BY
    author_date
    '''
    daily_commit_count = []
    for e in fetch_from_duckdb(sql, db):
        daily_commit_count.append({
            'date': e[0],
            'commit_count': e[1],
        })

    return daily_commit_count

def get_author_daily_contributions(email, proj, db):
    daily_contributions = []
    for e in fetch_from_duckdb(
        f''' select author_date,
        SUM(daily_commit_count) as daily_commit_count,
        SUM(insertions) as daily_insertions,
        SUM(deletions) as daily_deletions,
        from author_daily_commits
        where project = '{proj.name}' and author_email = '{email}'
        group by author_date order by author_date;
        ''',
            db
    ):
        daily_contributions.append({
            'author_date': e[0],
            'daily_commit_count': e[1],
            'daily_insertions': e[2],
            'daily_deletionts': e[3],
        })
    return daily_contributions


def index(request):
    res = []

    proj = request.GET.get('proj', '')
    force = True if request.GET.get('force', '') == '1' else False

    for p in Project.objects.all():
        if proj and p.name == proj:
            res.append(get_a_project_stat(p, force=force))

    return JsonResponse(res, safe=False)
