import datetime

import pytz
from django.conf import settings
from django.shortcuts import render
from django.utils.timezone import make_aware
from rest_framework.decorators import api_view
import pandas as pd

from projects.models import Project, ProjectActiviy
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

    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')

    native_dt = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    native_start_dt = native_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    native_dt = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    native_end_dt = native_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
    start_date = make_aware(native_start_dt, timezone=pytz.timezone(settings.TIME_ZONE))
    end_date = make_aware(native_end_dt, timezone=pytz.timezone(settings.TIME_ZONE))

    qs = ProjectActiviy.objects.filter(
        project__in=projs, author_datetime__gt=start_date, author_datetime__lt=end_date
    ).order_by('author_datetime')
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
