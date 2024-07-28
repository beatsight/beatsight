import datetime

import pytz
from django.conf import settings
from django.shortcuts import render
from django.utils.timezone import make_aware
from django.http import HttpResponse
from django.utils.timezone import localtime
from rest_framework.decorators import api_view
import pandas as pd

from projects.models import Project, ProjectActiviy
from developers.models import Developer
from beatsight.utils.response import ok, client_error, server_error


@api_view(['GET'])
def projects(request):
    names = request.GET.get('names', '')
    if not names:
        return client_error('names 不能为空')

    combined = request.GET.get('combined', '1') == '1'

    projs = []
    names = sorted([name.strip() for name in names.split(',')])
    for name in names:
        try:
            projs.append(Project.objects.get(name=name))
        except Project.DoesNotExist:
            return client_error(f"{name} 不存在")

    qs = ProjectActiviy.objects.filter(project__in=projs)

    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')
    if start_date and end_date:
        native_dt = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        native_start_dt = native_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        native_dt = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        native_end_dt = native_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
        start_date = make_aware(native_start_dt, timezone=pytz.timezone(settings.TIME_ZONE))
        end_date = make_aware(native_end_dt, timezone=pytz.timezone(settings.TIME_ZONE))

        qs = qs.filter(author_datetime__gt=start_date, author_datetime__lt=end_date)

    qs = qs.order_by('author_datetime')

    data = []
    author_names = {}
    for e in qs:
        author_names[e.author_email] = e.author_name
        data.append({
            'project': e.project.name,
            'commit_sha': e.commit_sha,
            'author_email': e.author_email,
            'author_datetime': e.author_datetime,
            'insertions': e.insertions,
            'deletions': e.deletions,
        })

    ret = []
    if not data:
        if not combined:
            for name in names:
                ret.append({
                    'project': name,
                    'commits': [],
                    'loc': [],
                })
        else:
            ret.append({
                'project': names,
                'commits': [],
                'loc': [],
            })
        return ok(ret)

    limit = 10
    df = pd.DataFrame(data)
    df['modifications'] = df['insertions'] + df['deletions']
    if not combined:
        grouped_df = df.groupby('project')

        proj_data = {}
        for name in names:
            proj_data[name] = {
                'commits': [],
                'loc': []
            }

        for project, group in grouped_df:
            subgroup = group.groupby('author_email')

            proj_data[project] = {
                'commits': [],
                'loc': [],
            }
            for email, count in subgroup['commit_sha'].count().sort_values(ascending=False).head(limit).items():
                data = {
                    'author': author_names[email],
                    'commits': count,
                }
                proj_data[project]['commits'].append(data)

            tmp = subgroup[['insertions', 'deletions', 'modifications']].sum().sort_values(by='modifications', ascending=False).head(limit)
            for author_email, row in tmp.iterrows():
                insertions = row['insertions']
                deletions = row['deletions']
                modifications = row['modifications']

                data = {
                    'author': author_names[author_email],
                    'modifications': modifications,
                    'insertions': insertions,
                    'deletions': deletions,
                }
                proj_data[project]['loc'].append(data)
        for proj, dic in proj_data.items():
            ret.append({
                'project': proj,
                'commits': dic['commits'],
                'loc': dic['loc']
            })
    else:
        group = df.groupby('author_email')

        commits = []
        loc = []
        for email, count in group['commit_sha'].count().sort_values(ascending=False).head(limit*2).items():
            data = {
                'author': author_names[email],
                'commits': count,
            }
            commits.append(data)

        tmp = group[['insertions', 'deletions', 'modifications']].sum().sort_values(by='modifications', ascending=False).head(limit*2)
        for author_email, row in tmp.iterrows():
            insertions = row['insertions']
            deletions = row['deletions']
            modifications = row['modifications']

            data = {
                'author': author_names[author_email],
                'modifications': modifications,
                'insertions': insertions,
                'deletions': deletions,
            }
            loc.append(data)

        ret.append({
            'project': names,
            'commits': commits,
            'loc': loc,
        })

    return ok(ret)

@api_view(['GET'])
def export_projects(request):
    names = request.GET.get('names', '')
    if not names:
        return client_error('names 不能为空')

    combined = request.GET.get('combined', '1') == '1'

    projs = []
    names = sorted([name.strip() for name in names.split(',')])
    for name in names:
        try:
            projs.append(Project.objects.get(name=name))
        except Project.DoesNotExist:
            return client_error(f"{name} 不存在")

    qs = ProjectActiviy.objects.filter(project__in=projs)

    start_date = request.GET.get('startDate', '')
    end_date = request.GET.get('endDate', '')
    if start_date and end_date:
        native_dt = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        native_start_dt = native_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        native_dt = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        native_end_dt = native_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
        start_date = make_aware(native_start_dt, timezone=pytz.timezone(settings.TIME_ZONE))
        end_date = make_aware(native_end_dt, timezone=pytz.timezone(settings.TIME_ZONE))

        qs = qs.filter(author_datetime__gt=start_date, author_datetime__lt=end_date)

    qs = qs.order_by('author_datetime')

    data = []
    author_names = {}
    for e in qs:
        author_names[e.author_email] = e.author_name
        data.append({
            'project': e.project.name,
            'commit_sha': e.commit_sha,
            'author_email': e.author_email,
            'author_datetime': e.author_datetime,
            'insertions': e.insertions,
            'deletions': e.deletions,
        })

    df = pd.DataFrame(data)
    df['modifications'] = df['insertions'] + df['deletions']

    if not combined:
        grouped_df = df.groupby('project')

        proj_dfs = {}
        for project, group in grouped_df:
            proj_df = (
                group
                .groupby('author_email')
                .agg(
                    commit_sha_count=('commit_sha', 'count'),
                    insertions_sum=('insertions', 'sum'),
                    deletions_sum=('deletions', 'sum'),
                    modifications_sum=('modifications', 'sum')
                )
                .reset_index()
                .sort_values(by='commit_sha_count', ascending=False)
            )
            proj_dfs[project] = proj_df

        # Create the Excel file in memory
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=project_report.xlsx'

        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            summary_df = pd.DataFrame({
                'projects': [';'.join(names)],
                'start date': [request.GET.get('startDate', '')],
                'end date': [request.GET.get('endDate', '')],
            })
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

            for proj, df in proj_dfs.items():
                df.to_excel(writer, sheet_name=proj, index=False)

        return response
    else:
        assert False

@api_view(['GET'])
def developers(request):
    emails = request.GET.get('emails', '')
    if not emails:
        return client_error('emails 不能为空')

    combined = request.GET.get('combined', '1') == '1'

    devs = []
    emails = sorted([name.strip() for name in emails.split(',')])
    for email in emails:
        try:
            devs.append(Developer.objects.get(email=email))
        except Developer.DoesNotExist:
            return client_error(f"{name} 不存在")

    qs = ProjectActiviy.objects.filter(author_email__in=emails)

    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')
    if start_date and end_date:
        native_dt = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        native_start_dt = native_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        native_dt = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        native_end_dt = native_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
        start_date = make_aware(native_start_dt, timezone=pytz.timezone(settings.TIME_ZONE))
        end_date = make_aware(native_end_dt, timezone=pytz.timezone(settings.TIME_ZONE))

        qs = qs.filter(author_datetime__gt=start_date, author_datetime__lt=end_date)

    qs = qs.order_by('author_datetime')

    data = []
    author_names = {}
    for e in qs:
        author_names[e.author_email] = e.author_name
        data.append({
            'project': e.project.name,
            'commit_sha': e.commit_sha,
            'author_email': e.author_email,
            'author_datetime': localtime(e.author_datetime),
            'insertions': e.insertions,
            'deletions': e.deletions,
        })

    ret = []
    if not data:
        assert False

    df = pd.DataFrame(data)
    df['modifications'] = df['insertions'] + df['deletions']
    df['author_datetime'] = pd.to_datetime(df['author_datetime'])

    delta_days = (df['author_datetime'].max() - df['author_datetime'].min()).days
    if delta_days <= 45:
        group_by = 'day'
    elif delta_days <= 350:
        group_by = 'week'
    else:
        group_by = 'month'

    def get_result_df(group_by):
        if group_by == 'day':
            df['date'] = df['author_datetime'].dt.date
            freq = 'D'
        elif group_by == 'week':
            df['date'] = df['author_datetime'].dt.to_period('W').dt.start_time
            freq = 'W-MON'
        else:
            df['date'] = df['author_datetime'].dt.to_period('M').dt.start_time
            freq = 'MS'

        result = (
            df.groupby(['author_email', 'date'])
            .agg({
                'commit_sha': 'count',
                'insertions': 'sum',
                'deletions': 'sum',
                'modifications': 'sum'
            })
            .reset_index()
            .rename(columns={
                'commit_sha': 'commit_count',
                'insertions': 'insertions',
                'deletions': 'deletions',
                'modifications': 'modifications'
            })
        )

        all_dates = pd.date_range(df['date'].min(), df['date'].max(), freq=freq).date
        all_combinations = pd.MultiIndex.from_product([result['author_email'].unique(), all_dates], names=['author_email', 'date'])
        # Reindex the DataFrame to include missing rows
        result = result.set_index(['author_email', 'date']).reindex(all_combinations, fill_value=0).reset_index()
        return result

    result = get_result_df(group_by)

    ret = []
    for author_email, author_group in result.groupby('author_email'):
        commits = []
        loc = []
        for date, row in author_group.iterrows():
            commits.append({'date': row['date'], 'commit_count': row['commit_count']})
            loc.append({'date': row['date'],
                        'insertions': row['insertions'], 'deletions': row['deletions'],
                        'modifications': row['modifications']})
        ret.append({
            'author': author_email,
            'commits': commits,
            'loc': loc
        })

    return ok(ret)
