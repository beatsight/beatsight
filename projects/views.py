import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404

from stats.models import GeneralData, ActivityData, AuthorData
from stats.utils import fetch_from_duckdb
from beatsight.utils import CustomJSONEncoder
from .models import Project, SimpleSerializer, DetailSerializer

def index(request):
    """list all projects"""
    res = []

    for p in Project.objects.all():
        try:
            gd = GeneralData.objects.get(project=p)
        except GeneralData.DoesNotExist:
            gd = None
        last_commit_date = gd.last_commit_date if gd else None

        try:
            ac = ActivityData.objects.get(project=p)
        except ActivityData.DoesNotExist:
            ac = None
        recent_weekly_activity = ac.recent_weekly_activity if ac else None

        ss = SimpleSerializer(
            p, last_commit_date=last_commit_date, recent_weekly_activity=recent_weekly_activity
        )
        res.append(ss.data)

    return JsonResponse(res, safe=False)
    # return HttpResponse(json.dumps(res, cls=CustomJSONEncoder),
    #                     content_type='application/json')

def detail(request, proj):
    """get a project detail"""
    p = get_object_or_404(Project, name=proj)

    try:
        gd = GeneralData.objects.get(project=p)
    except GeneralData.DoesNotExist:
        gd = None
    last_commit_date = gd.last_commit_date if gd else None

    try:
        ac = ActivityData.objects.get(project=p)
    except ActivityData.DoesNotExist:
        ac = None
    recent_weekly_activity = ac.recent_weekly_activity if ac else None

    try:
        au = AuthorData.objects.get(project=p)
    except AuthorData.DoesNotExist:
        au = None
    top_authors_statistics = au.authors_statistics[:10] if au else None

    s = DetailSerializer(
        p, last_commit_date=last_commit_date, recent_weekly_activity=recent_weekly_activity,
        top_authors_statistics=top_authors_statistics
    )
    return JsonResponse(s.data, safe=False)
    # return HttpResponse(json.dumps(res), content_type='application/json')

def contributors(request, proj):
    """get contributors of a project"""
    p = get_object_or_404(Project, name=proj)

    try:
        au = AuthorData.objects.get(project=p)
    except AuthorData.DoesNotExist:
        assert False, 'TODO: no author data'

    res = []
    for e in au.authors_statistics:
        data = fetch_from_duckdb(
            f'''select * from author_daily_commits where project = '{p.name}' and author_email = '{e["author_email"]}' order by author_date'''
        )
        e['commit_distribution'] = data
        res.append(e)

    # data = fetch_from_duckdb(
    #     "select author_email, sum(daily_commit_count) as daily_commit_count_sum from author_daily_commits "
    #     f"where project = '{p.name}' group by author_email order by daily_commit_count_sum desc"
    # )

    # res = []
    # for row in data:
    #     res.append({
    #         'author_email': row[0],
    #         'commit_count_sum': row[1],
    #     })

    # for e in res:
    #     data = fetch_from_duckdb(
    #         f'''select * from author_daily_commits where project = '{p.name}' and author_email = '{e["author_email"]}' order by author_date'''
    #     )
    #     e['commit_distribution'] = data

    return JsonResponse(res, safe=False)
