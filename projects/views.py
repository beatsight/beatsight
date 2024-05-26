import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404

from stats.models import GeneralData, ActivityData, AuthorData, AuthorDataSerializer
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
        last_commit_at = gd.last_commit_at if gd else None

        try:
            ac = ActivityData.objects.get(project=p)
        except ActivityData.DoesNotExist:
            ac = None
        recent_weekly_activity = ac.recent_weekly_activity if ac else None

        ss = SimpleSerializer(
            p, last_commit_at=last_commit_at, recent_weekly_activity=recent_weekly_activity
        )
        res.append(ss.data)

    return JsonResponse(res, safe=False)
    # return HttpResponse(json.dumps(res, cls=CustomJSONEncoder),
    #                     content_type='application/json')

def detail(request, proj):
    """get detail of a project (recent activity, top authors ...)"""
    p = get_object_or_404(Project, name=proj)

    try:
        gd = GeneralData.objects.get(project=p)
    except GeneralData.DoesNotExist:
        gd = None
    last_commit_at = gd.last_commit_at if gd else None

    try:
        ac = ActivityData.objects.get(project=p)
    except ActivityData.DoesNotExist:
        ac = None
    recent_weekly_activity = ac.recent_weekly_activity if ac else None

    authors = []
    for e in AuthorData.objects.filter(project=p):
        authors.append(AuthorDataSerializer(e).data)

    top_authors_statistics = authors[:10]

    s = DetailSerializer(
        p, last_commit_at=last_commit_at, recent_weekly_activity=recent_weekly_activity,
        top_authors_statistics=top_authors_statistics
    )
    return JsonResponse(s.data, safe=False)
    # return HttpResponse(json.dumps(res), content_type='application/json')

def contributors(request, proj):
    """get authors' contribution distribution of a project"""
    p = get_object_or_404(Project, name=proj)

    res = []
    for e in AuthorData.objects.filter(project=p):
        data = AuthorDataSerializer(e).data
        data['commit_distribution'] = []
        for ee in fetch_from_duckdb(
            f''' select author_date, SUM(daily_commit_count) as daily_commit_count
            from author_daily_commits
            where project = '{p.name}' and author_email = '{e.author_email}'
            group by author_date order by author_date;
            '''
        ):
            data['commit_distribution'].append({
                'author_date': ee[0],
                'daily_commit_count': ee[1],
            })
        res.append(data)

    return JsonResponse(res, safe=False)
