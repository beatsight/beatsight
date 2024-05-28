from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse

from stats.utils import fetch_from_duckdb
from projects.models import SimpleSerializer as ProjectSimpleSerializer
from beatsight.utils import recent_weekly_commit_count

from .models import Developer, SimpleSerializer, DetailSerializer

def get_recent_weekly_commit_count(email):
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

    return recent_weekly_commit_count(weekly_commit_count)

def index(request):
    """list all developers"""
    res = []
    for e in Developer.objects.all():
        commit_count = get_recent_weekly_commit_count(e.email)
        res.append(SimpleSerializer(e, recent_weekly_activity=commit_count).data)

    return JsonResponse(res, safe=False)

def detail(request, email):
    """get detail of a developer (recent activity, top projects ...)"""
    d = get_object_or_404(Developer, email=email)

    commit_count = get_recent_weekly_commit_count(email)
    res = DetailSerializer(d, recent_weekly_activity=commit_count).data

    return JsonResponse(res, safe=False)

def projects(request, email):
    """get projects' contribution distribution of a developer"""
    d = get_object_or_404(Developer, email=email)

    res = []
    for proj in d.projects.all():
        data = ProjectSimpleSerializer(proj).data
        data['commit_distribution'] = []
        for ee in fetch_from_duckdb(
            f''' select author_date, SUM(daily_commit_count) as daily_commit_count
            from author_daily_commits
            where project = '{proj.name}' and author_email = '{email}'
            group by author_date order by author_date;
            '''
        ):
            data['commit_distribution'].append({
                'author_date': ee[0],
                'daily_commit_count': ee[1],
            })
        res.append(data)

    return JsonResponse(res, safe=False)
