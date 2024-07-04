import json

import pandas as pd
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse

from projects.models import SimpleSerializer as ProjectSimpleSerializer

from .models import Developer, SimpleSerializer, DetailSerializer, DeveloperContribution, DeveloperContributionSerializer


def index(request):
    """list all developers"""
    res = []
    for e in Developer.objects.all():
        res.append(SimpleSerializer(e).data)

    return JsonResponse(res, safe=False)

def detail(request, email):
    """get detail of a developer (recent activity, top projects ...)"""
    d = get_object_or_404(Developer, email=email)

    res = DetailSerializer(d).data

    commits_total = sum(e['commits_count'] for e in res['contribution'])

    for e in res['contribution']:
        e['percentage'] = round(e['commits_count'] / commits_total * 100, 1)

    return JsonResponse(res, safe=False)

def contributions(request, email):
    """get projects' contribution distribution of a developer"""
    d = get_object_or_404(Developer, email=email)

    res = []
    for e in DeveloperContribution.objects.filter(developer=d):
        serializer = DeveloperContributionSerializer(e)
        res.append(serializer.data)

    return JsonResponse(res, safe=False)
