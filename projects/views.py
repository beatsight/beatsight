import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404

from stats.models import GeneralData, ActivityData, AuthorData, AuthorDataSerializer
from stats.utils import fetch_from_duckdb
from beatsight.utils import CustomJSONEncoder

from developers.models import DeveloperContribution, DeveloperContributionSerializer
from .models import Project, SimpleSerializer, DetailSerializer
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def index(request):
    """list all projects"""
    if request.method == 'POST':
        req_data = json.loads(request.body)
        repo_url = req_data['repo_url'].strip()
        name = req_data['name'].strip()
        repo_branch = req_data['repo_branch'].strip()

        p = Project(name=name, repo_url=repo_url, repo_path='', branch=repo_branch)
        p.save()
        p.refresh_from_db()

        res = SimpleSerializer(p).data
        return JsonResponse(res, safe=False)


    # get
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
    print(res)
    return JsonResponse(res, safe=False)
    # return HttpResponse(json.dumps(res, cls=CustomJSONEncoder),
    #                     content_type='application/json')

@csrf_exempt
def detail(request, proj):
    """get detail of a project (recent activity, top authors ...)"""
    p = get_object_or_404(Project, name=proj)
    if request.method == 'DELETE':
        p.delete()
        return JsonResponse({})

    elif request.method == 'POST':
        req_data = json.loads(request.body)
        p.name = req_data['name'].strip()
        p.repo_url = req_data['repo_url'].strip()
        p.repo_branch = req_data['repo_branch'].strip()
        p.save()
        p.refresh_from_db()

        res = SimpleSerializer(p).data
        return JsonResponse(res, safe=False)


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
    for e in DeveloperContribution.objects.filter(project=p):
        serializer = DeveloperContributionSerializer(e)
        res.append(serializer.data)

    return JsonResponse(res, safe=False)
