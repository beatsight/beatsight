import json
import sys
from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.utils.timezone import get_current_timezone
import pandas as pd

from projects.models import Project
from developers.models import Developer
from stats.models import (
    GeneralData, GeneralDataSerializer, ActivityData, ActivityDataSerializer,
    AuthorData, AuthorDataSerializer,
    # FileData, FileDataSerializer,
)
from vendor.repostat.analysis.gitrepository import GitRepository

from .utils import save_dataframe_to_duckdb, delete_dataframes_from_duckdb, fetch_from_duckdb

def get_a_project_stat(p: Project, force=False):
    """Get stat data of a project."""
    gen_new = False
    if force is True:
        last_sync_commit = ''
        gen_new = True

    if p.head_commit != p.last_stat_commit:
        last_sync_commit = p.last_stat_commit
        gen_new = True

    if gen_new:
        # get whole/partial repo history
        repo = GitRepository(p.repo_path, prev_commit_oid=last_sync_commit)

        # save repo history df
        replace_or_append = 'replace' if last_sync_commit == '' else 'append'
        save_dataframe_to_duckdb(repo.whole_history_df, f"{p.name}", replace_or_append)
        # save current commit as last stat commit
        p.last_stat_commit = p.head_commit
        p.save()

        ### general data
        try:
            gd = GeneralData.objects.get(project=p)
        except GeneralData.DoesNotExist:
            gd = GeneralData(project=p)

        gd.files_count = repo.head.files_count

        sql = f''' SELECT
  commit_sha,
  author_timestamp
FROM
  {p.name}
ORDER BY
  author_timestamp ASC
LIMIT 1;
        '''
        res = fetch_from_duckdb(sql)
        assert len(res) == 1
        gd.first_commit_id, gd.first_commit_at = res[0][0], timezone.make_aware(datetime.fromtimestamp(res[0][1]))

        sql = f''' SELECT
  commit_sha,
  author_timestamp
FROM
  {p.name}
ORDER BY
  author_timestamp DESC
LIMIT 1;
        '''
        res = fetch_from_duckdb(sql)
        assert len(res) == 1
        gd.last_commit_id, gd.last_commit_at = res[0][0], timezone.make_aware(datetime.fromtimestamp(res[0][1]))
        gd.age = (gd.last_commit_at - gd.first_commit_at).days

        sql = f''' SELECT
  COUNT(*) AS total_commits,
  COUNT(DISTINCT DATE_TRUNC('day', TO_TIMESTAMP(author_timestamp))) AS active_days_count
FROM
  {p.name};
'''
        res = fetch_from_duckdb(sql)
        assert len(res) == 1
        gd.commits_count, gd.active_days_count = res[0]
        gd.save()

        ### activity stata (past year activity, month_in_year/weekday/hourly activiy )
        # activity_data = data['activity']
        try:
            ac = ActivityData.objects.get(project=p)
        except ActivityData.DoesNotExist:
            ac = ActivityData(project=p)

        sql = f'''SELECT
    DATE_TRUNC('week', TO_TIMESTAMP(author_timestamp)) AS week,
    COUNT(commit_sha) AS commit_count
FROM {p.name}
GROUP BY week
ORDER BY week;
        '''
        weekly_activity = []
        for e in fetch_from_duckdb(sql):
            weekly_activity.append({
                'week': e[0],
                'commit_count': e[1],
            })
        ac.weekly_activity = weekly_activity

        sql = f'''SELECT
    DATE_TRUNC('month', TO_TIMESTAMP(author_timestamp)) AS month,
    COUNT(commit_sha) AS commit_count
FROM {p.name}
GROUP BY month
ORDER BY month;
        '''
        monthly_activity = []
        for e in fetch_from_duckdb(sql):
            monthly_activity.append({
                'month': e[0],
                'commit_count': e[1],
            })
        ac.monthly_activity = monthly_activity

        sql = f'''SELECT
    DATE_TRUNC('year', TO_TIMESTAMP(author_timestamp)) AS year,
    COUNT(commit_sha) AS commit_count
FROM {p.name}
GROUP BY year
ORDER BY year;
        '''
        yearly_activity = []
        for e in fetch_from_duckdb(sql):
            yearly_activity.append({
                'year': e[0],
                'commit_count': e[1],
            })
        ac.yearly_activity = yearly_activity
        ac.save()

        ### authors stat (insertions, deletions, commits_count, active_days_count ...)
        # author_data = data['authors']

        sql = f'''
        SELECT author_email,
        FIRST(author_name) AS author_name,
        COUNT(*) AS commit_count,
        CAST(TO_TIMESTAMP(min(author_timestamp)) AS DATETIME) AS first_commit_datetime,
        CAST(TO_TIMESTAMP(max(author_timestamp)) AS DATETIME) AS lastest_commit_datetime,
        FROM {p.name}
        GROUP BY author_email
        ORDER BY commit_count DESC;
        '''
        for e in fetch_from_duckdb(sql):
            try:
                au = AuthorData.objects.get(project=p, author_email=e[0])
            except AuthorData.DoesNotExist:
                au = AuthorData(project=p, author_email=e[0])

            au.author_email, au.author_name, au.commit_count = e[0], e[1], e[2]
            au.first_commit_date, au.last_commit_date = timezone.make_aware(e[3]), timezone.make_aware(e[4])
            au.contributed_days = (au.last_commit_date - au.first_commit_date).days + 1
            au.save()

            try:
                de = Developer.objects.get(email=au.author_email)
            except Developer.DoesNotExist:
                de = Developer(email=au.author_email)
            de.name = au.author_name
            de.set_first_last_commit_at(au.first_commit_date, au.last_commit_date)
            de.save()
            de.add_a_project(p)

        ## Do not stat files count/size for the moment
        # ### files stat (file type, size, count, lines count)
        # files_data = data['files']
        # if fd is None:
        #     fd = FileData(project=p)
        # fd.file_summary = files_data['file_summary']
        # fd.total_files_count = files_data['total_files_count']
        # fd.total_lines_count = files_data['total_lines_count']
        # fd.save()
        # fd_s = FileDataSerializer(fd)

        # save user daily commits count df
        # should be calculated in local timezones
        df = repo.whole_history_df
        df['author_date'] = pd.to_datetime(df['author_timestamp'], unit='s', utc=True) + \
            pd.TimedeltaIndex(df['author_tz_offset'], unit='m')
        df['author_date'] = df['author_date'].dt.date

        author_commit_counts = df.groupby(['author_email', 'author_date']).size().reset_index(name='daily_commit_count')
        author_commit_counts = author_commit_counts[author_commit_counts['daily_commit_count'] > 0]
        author_commit_counts['project'] = p.name

        if last_sync_commit == '':
            delete_dataframes_from_duckdb("author_daily_commits", f"project='{p.name}'")
        save_dataframe_to_duckdb(author_commit_counts, "author_daily_commits", "append")

    # show the data
    gd_s = GeneralDataSerializer(gd)
    ac_s = ActivityDataSerializer(ac)
    author_data = []
    for e in AuthorData.objects.filter(project=p):
        author_data.append(AuthorDataSerializer(e).data)

    return {
        'general': gd_s.data,
        'activity': ac_s.data,
        'authors': author_data,
        # 'files': fd_s.data if fd_s else {},
    }


def index(request):
    res = []

    proj = request.GET.get('proj', '')
    force = True if request.GET.get('force', '') == '1' else False

    for p in Project.objects.all():
        if proj and p.name == proj:
            res.append(get_a_project_stat(p, force=force))

    return JsonResponse(res, safe=False)
