import json
import sys
from datetime import datetime
from collections import defaultdict

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.utils.timezone import get_current_timezone
import pandas as pd

from beatsight.utils.pl_ext import PL_EXT
from projects.models import Project
from developers.models import Developer, Language, DeveloperLanguage, DeveloperContribution
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
                dev = Developer.objects.get(email=au.author_email)
            except Developer.DoesNotExist:
                dev = Developer(email=au.author_email)
            dev.name = au.author_name
            dev.set_first_last_commit_at(au.first_commit_date, au.last_commit_date)
            dev.total_commits = au.commit_count
            dev.save()
            dev.add_a_project(p)

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

        # Group by author_email and date, then calculate the sum of insertions and deletions
        daily_stats = df.groupby(['author_email', 'author_date']).agg({
            'insertions': 'sum',
            'deletions': 'sum',
            'commit_sha': 'count',
            'file_exts': lambda x: ';'.join(list(set(sum(x, [])))),
        }).reset_index()
        daily_stats.columns = ['author_email', 'author_date', 'insertions', 'deletions', 'daily_commit_count', 'file_exts']
        daily_stats = daily_stats[daily_stats['daily_commit_count'] > 0]
        daily_stats['project'] = p.name
        if last_sync_commit == '':
            delete_dataframes_from_duckdb("author_daily_commits", f"project='{p.name}'")
        save_dataframe_to_duckdb(daily_stats, "author_daily_commits", "append")

        # calculate authors' activities, most used languages, contributions
        for email in daily_stats['author_email'].unique().tolist():
            dev = Developer.objects.get(email=email)
            if dev is None:
                # raise warning
                continue

            dev.daily_activity = get_author_daily_commit_count(email)
            dev.weekly_activity = get_author_weekly_commit_count(email)
            dev.save()

            for lang, cnt in get_most_used_langs(email):
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

            try:
                dev_contrib = DeveloperContribution.objects.get(developer=dev, project=p)
            except DeveloperContribution.DoesNotExist:
                dev_contrib = DeveloperContribution(developer=dev, project=p)
            dev_contrib.daily_contribution = get_author_daily_contributions(email, p)
            dev_contrib.save()

            dev.calculate_rank()

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


## user related
def get_most_used_langs(email):
    sql = f"""
    select file_exts from author_daily_commits where author_email = '{email}'
    """
    file_exts_df = fetch_from_duckdb(sql, to_df=True)

    tmp = pd.DataFrame([x for row in file_exts_df['file_exts'] for x in row.split(';')], columns=['file_ext'])
    top_file_exts = tmp.groupby('file_ext').size().sort_values(ascending=False).head(10)
    lang_cnt = defaultdict(int)
    for fe, count in top_file_exts.items():
        if fe not in PL_EXT:
            continue
        lang_cnt[PL_EXT[fe]] += count

    # # Calculate the total count
    # total_count = sum(lang_cnt.values())

    return lang_cnt.items()

    # for key, value in
    #     percentage = (value / total_count) * 100
    #     top_langs[key] = f"{percentage:.2f}%"
    # return top_langs

def get_author_weekly_commit_count(email):
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
    for e in fetch_from_duckdb(sql):
        weekly_commit_count.append({
            'week': e[0],
            'commit_count': e[1],
        })

    return weekly_commit_count

def get_author_daily_commit_count(email):
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
    for e in fetch_from_duckdb(sql):
        daily_commit_count.append({
            'date': e[0],
            'commit_count': e[1],
        })

    return daily_commit_count

def get_author_daily_contributions(email, proj):
    daily_contributions = []
    for e in fetch_from_duckdb(
        f''' select author_date,
        SUM(daily_commit_count) as daily_commit_count,
        SUM(insertions) as daily_insertions,
        SUM(deletions) as daily_deletions,
        from author_daily_commits
        where project = '{proj.name}' and author_email = '{email}'
        group by author_date order by author_date;
        '''
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
