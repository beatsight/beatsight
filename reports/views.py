from django.shortcuts import render
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
    for name in names.split(','):
        name = name.strip()
        try:
            projs.append(Project.objects.get(name=name))
        except Project.DoesNotExist:
            return client_error(f"{name} 不存在")

    qs = ProjectActiviy.objects.filter(project__in=projs)
    data = []
    for e in qs:
        data.append({
            'project': e.project.name,
            'commit_sha': e.commit_sha,
            'author_email': e.author_email,
            'author_datetime': e.author_datetime,
            'insertions': e.insertions,
            'deletions': e.deletions,
        })

# uncombined: [
#   {
#     project: xxx,
#     commits: [{author, count}],
#     modifications: [{author, modifications, insertions, deletions}]
#   }
# ]


# combined: [
#   {
#     project: xxx,yyy,
#     commits: [{author, count}],
#     modifications: [{author, modifications, insertions, deletions}]
#   }
# ]

    # ret = {
    #     'combined': [],
    #     'uncombined': [],
    # }
    ret = []

    df = pd.DataFrame(data)
    df['modifications'] = df['insertions'] + df['deletions']
    if not combined:
        grouped_df = df.groupby('project')

        proj_data = {}
        for project, group in grouped_df:
            subgroup = group.groupby('author_email')

            proj_data[project] = {
                'commits': [],
                'loc': [],
            }
            for email, count in subgroup['commit_sha'].count().sort_values(ascending=False).items():
                data = {
                    'author': email,
                    'commits': count,
                }
                proj_data[project]['commits'].append(data)

            tmp = subgroup[['insertions', 'deletions', 'modifications']].sum().sort_values(by='modifications', ascending=False)
            for author_email, row in tmp.iterrows():
                insertions = row['insertions']
                deletions = row['deletions']
                modifications = row['modifications']

                data = {
                    'author': author_email,
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
        for email, count in group['commit_sha'].count().sort_values(ascending=False).items():
            data = {
                'author': email,
                'commits': count,
            }
            commits.append(data)

        tmp = group[['insertions', 'deletions', 'modifications']].sum().sort_values(by='modifications', ascending=False)
        for author_email, row in tmp.iterrows():
            insertions = row['insertions']
            deletions = row['deletions']
            modifications = row['modifications']

            data = {
                'author': author_email,
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
