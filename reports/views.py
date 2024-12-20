"""
This file is part of Beatsight.

Copyright (C) 2024-2025 Beatsight Ltd.
Licensed under the GNU General Public License v3.0.
"""

import datetime

import pytz
from django.conf import settings
from django.shortcuts import render
from django.utils.timezone import make_aware
from django.http import HttpResponse
from django.utils.timezone import localtime
from django.utils.translation import gettext as _
from rest_framework.decorators import api_view
import pandas as pd

from projects.models import Project, ProjectActivity
from developers.models import Developer
from beatsight.utils.response import ok, client_error, server_error


@api_view(['GET'])
def projects(request):
    names = request.GET.get('names', '')
    if not names:
        return client_error(_('names cannot be empty'))

    combined = request.GET.get('combined', '1') == '1'

    projs = []
    names = sorted([name.strip() for name in names.split(',')])
    for name in names:
        try:
            projs.append(Project.objects.get(name=name))
        except Project.DoesNotExist:
            return client_error(f"{name} 不存在")

    qs = ProjectActivity.objects.filter(project__in=projs)

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
            'insertions': e.corrected_insertions,
            'deletions': e.corrected_deletions,
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

            tmp = subgroup[
                ['insertions', 'deletions', 'modifications']
            ].sum().sort_values(by='modifications', ascending=False).head(limit)
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
        for email, count in group['commit_sha'].count().sort_values(ascending=False).head(limit * 2).items():
            data = {
                'author': author_names[email],
                'commits': count,
            }
            commits.append(data)

        tmp = group[['insertions', 'deletions', 'modifications']].sum().sort_values(by='modifications', ascending=False).head(limit * 2)
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
        return client_error(_('names cannot be empty'))

    combined = request.GET.get('combined', '1') == '1'

    projs = []
    names = sorted([name.strip() for name in names.split(',')])
    for name in names:
        try:
            projs.append(Project.objects.get(name=name))
        except Project.DoesNotExist:
            return client_error(f"{name} 不存在")

    qs = ProjectActivity.objects.filter(project__in=projs)

    start_date_str = request.GET['startDate']
    end_date_str = request.GET['endDate']
    if start_date_str and end_date_str:
        native_dt = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
        native_start_dt = native_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        native_dt = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')
        native_end_dt = native_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
        start_date = make_aware(native_start_dt, timezone=pytz.timezone(settings.TIME_ZONE))
        end_date = make_aware(native_end_dt, timezone=pytz.timezone(settings.TIME_ZONE))

        qs = qs.filter(author_datetime__gt=start_date, author_datetime__lt=end_date)
    else:
        assert False

    qs = qs.order_by('author_datetime')

    data = []
    author_names = {}
    author_emails = set()
    for e in qs:
        author_names[e.author_email] = e.author_name
        author_emails.add(e.author_email)
        data.append({
            'project': e.project.name,
            'commit_sha': e.commit_sha,
            'author_email': e.author_email,
            'author_datetime': e.author_datetime,
            'insertions': e.insertions,
            'deletions': e.deletions,
            'corrected_insertions': e.corrected_insertions,
            'corrected_deletions': e.corrected_deletions,
        })

    df = pd.DataFrame(data)
    df['modifications'] = df['insertions'] + df['deletions']
    df['corrected_modifications'] = df['corrected_insertions'] + df['corrected_deletions']

    if not combined:
        grouped_df = df.groupby('project')

        proj_dfs = {}
        for project, group in grouped_df:
            proj_df = (
                group
                .groupby('author_email')
                .agg(
                    commit_sha_count=('commit_sha', 'count'),
                    insertions=('insertions', 'sum'),
                    deletions=('deletions', 'sum'),
                    modifications=('modifications', 'sum'),
                    corrected_insertions=('corrected_insertions', 'sum'),
                    corrected_deletions=('corrected_deletions', 'sum'),
                    corrected_modifications=('corrected_modifications', 'sum'),
                )
                .reset_index()
                .sort_values(by='commit_sha_count', ascending=False)
                .rename(columns={
                    'commit_sha_count': _('# of commits'),
                    'insertions': _('add LOC'),
                    'deletions': _('delete LOC'),
                    'modifications': _('modify LOC'),
                    'corrected_insertions': _('(valid) add LOC'),
                    'corrected_deletions': _('(valid) delete LOC'),
                    'corrected_modifications': _('(valid) modify LOC'),
                })
            )
            proj_dfs[project] = proj_df

        # Create the Excel file in memory
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=project_report-{start_date_str}_{end_date_str}.xlsx'

        with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
            data = {
                _('projects'): names,
                _('developers'): list(author_emails),
                _('start date'): [start_date_str],
                _('end date'): [end_date_str],
            }
            max_length = max(len(names), len(author_emails))
            filled_data = {k: v + [''] * (max_length - len(v)) for k, v in data.items()}
            summary_df = pd.DataFrame(filled_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            for col_idx in [0, 1, 2]:
                writer.sheets['Summary'].set_column(col_idx, col_idx, 15)

            for proj, df in proj_dfs.items():
                df.to_excel(writer, sheet_name=proj, index=False)
                for col_idx in [0, 5, 6, 7]:
                    writer.sheets[proj].set_column(col_idx, col_idx, 15)

        return response
    else:
        assert False

@api_view(['GET'])
def developers(request):
    emails = request.GET.get('emails', '')
    if not emails:
        return client_error(_('emails cannot be empty'))

    combined = request.GET.get('combined', '1') == '1'

    devs = []
    emails = sorted([name.strip() for name in emails.split(',')])
    for email in emails:
        try:
            devs.append(Developer.objects.get(email=email))
        except Developer.DoesNotExist:
            return client_error(_(f"{email} does not exist"))

    qs = ProjectActivity.objects.filter(author_email__in=emails)

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
            'insertions': e.corrected_insertions,
            'deletions': e.corrected_deletions,
        })

    ret = []
    if not data:
        for email in emails:
            ret.append({
                'author': email,
                'commits': [],
                'loc': [],
            })
        return ok(ret)

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

    author_data = {}
    for email in emails:
        author_data[email] = {
            'commits': [],
            'loc': [],
        }

    ret = []
    for author_email, author_group in result.groupby('author_email'):
        commits = []
        loc = []
        for date, row in author_group.iterrows():
            commits.append({'date': row['date'], 'commit_count': row['commit_count']})
            loc.append({'date': row['date'],
                        'insertions': row['insertions'], 'deletions': row['deletions'],
                        'modifications': row['modifications']})
        author_data[author_email] = {
            'commits': commits,
            'loc': loc
        }
    for author_email, dic in author_data.items():
        ret.append({
            'author': author_email,
            'commits': dic['commits'],
            'loc': dic['loc'],
        })

    return ok(ret)

@api_view(['GET'])
def export_developers(request):
    emails = request.GET.get('emails', '')
    if not emails:
        return client_error(_('emails cannot be empty'))

    combined = request.GET.get('combined', '1') == '1'

    devs = []
    emails = sorted([name.strip() for name in emails.split(',')])
    for email in emails:
        try:
            devs.append(Developer.objects.get(email=email))
        except Developer.DoesNotExist:
            return client_error(_(f"{email} does not exist"))

    qs = ProjectActivity.objects.filter(author_email__in=emails)

    start_date_str = request.GET['startDate']
    end_date_str = request.GET['endDate']
    if start_date_str and end_date_str:
        native_dt = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
        native_start_dt = native_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        native_dt = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')
        native_end_dt = native_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
        start_date = make_aware(native_start_dt, timezone=pytz.timezone(settings.TIME_ZONE))
        end_date = make_aware(native_end_dt, timezone=pytz.timezone(settings.TIME_ZONE))

        qs = qs.filter(author_datetime__gt=start_date, author_datetime__lt=end_date)
    else:
        assert False

    qs = qs.order_by('author_datetime')

    data = []
    author_names = {}
    projects = set()
    for e in qs:
        author_names[e.author_email] = e.author_name
        projects.add(e.project.name)
        data.append({
            'project': e.project.name,
            'commit_sha': e.commit_sha,
            'author_email': e.author_email,
            'author_datetime': localtime(e.author_datetime),
            'insertions': e.insertions,
            'deletions': e.deletions,
            'corrected_insertions': e.corrected_insertions,
            'corrected_deletions': e.corrected_deletions,
        })

    ret = []
    if not data:
        assert False

    df = pd.DataFrame(data)
    df['modifications'] = df['insertions'] + df['deletions']
    df['corrected_modifications'] = df['corrected_insertions'] + df['corrected_deletions']
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
                'modifications': 'sum',
                'corrected_insertions': 'sum',
                'corrected_deletions': 'sum',
                'corrected_modifications': 'sum'
            })
            .reset_index()
            .rename(columns={
                # 'author_email': '开发人员',
                # 'date': '日期',
                'commit_sha_count': _('# of commits'),
                'insertions': _('add LOC'),
                'deletions': _('delete LOC'),
                'modifications': _('modify LOC'),
                'corrected_insertions': _('(valid) add LOC'),
                'corrected_deletions': _('(valid) delete LOC'),
                'corrected_modifications': _('(valid) modify LOC'),
            })
        )

        all_dates = pd.date_range(df['date'].min(), df['date'].max(), freq=freq).date
        all_combinations = pd.MultiIndex.from_product([result['author_email'].unique(), all_dates], names=['author_email', 'date'])
        # Reindex the DataFrame to include missing rows
        result = result.set_index(['author_email', 'date']).reindex(all_combinations, fill_value=0).reset_index()
        return result

    result = get_result_df(group_by)

    author_dfs = {}
    for email in emails:
        author_dfs[email] = pd.DataFrame()

    for author_email, author_group in result.groupby('author_email'):
        author_dfs[author_email] = author_group

    # Create the Excel file in memory
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=developer_report-{start_date_str}_{end_date_str}.xlsx'

    with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
        data = {
            _('developers'): emails,
            _('projects'): list(projects),
            _('start date'): [start_date_str],
            _('end date'): [end_date_str],
        }
        max_length = max(len(emails), len(projects))
        filled_data = {k: v + [''] * (max_length - len(v)) for k, v in data.items()}
        summary_df = pd.DataFrame(filled_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        for col_idx in [0, 1, 2]:
            writer.sheets['Summary'].set_column(col_idx, col_idx, 15)

        for author, df in author_dfs.items():
            sheet_name = author[:30]
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            for col_idx in [0, 1, 6, 7, 8]:
                writer.sheets[sheet_name].set_column(col_idx, col_idx, 15)

    return response
