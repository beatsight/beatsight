import json
from collections import defaultdict
import datetime

import pandas as pd
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view

from projects.models import SimpleSerializer as ProjectSimpleSerializer
from projects.models import ProjectActiviy, ProjectActiviySerializer
from beatsight.pagination import CustomPagination
from beatsight.utils.response import ok

from .models import Developer, SimpleSerializer, DetailSerializer, DeveloperContribution, DeveloperContributionSerializer


def index(request):
    """list all developers"""
    res = []
    for e in Developer.objects.all().order_by('rank_percentile')[:100]:
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

@api_view(['GET'])
def activities(request, email):
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')


    qs = ProjectActiviy.objects.filter(author_email=email).order_by(
        '-author_datetime'
    )

    pnp = CustomPagination()
    page = pnp.paginate_queryset(qs, request)
    s = ProjectActiviySerializer(page, many=True)

    res = defaultdict(list)
    for e in s.data:
        dt = e['author_datetime'].split('T')[0]
        res[dt].append(e)

    data = []
    for k, lst in res.items():
        data.append({
            'date': k,
            'result': lst
        })

    return pnp.get_paginated_response(data)

@api_view(['GET'])
def contrib_calendar(request, email):
    today = timezone.now().date()
    one_year_ago = today - datetime.timedelta(days=366)

    res = {}
    current_date = one_year_ago
    while current_date <= today:
        date_str = current_date.strftime('%Y-%m-%d')
        res[date_str] = []
        current_date += datetime.timedelta(days=1)

    for e in ProjectActiviy.objects.filter(author_email=email, author_datetime__gt=one_year_ago):
        date_str = e.author_datetime.strftime('%Y-%m-%d')
        res[date_str].append(e.commit_sha)

    data = []
    for date_str, val in res.items():
        cnt = len(val)

        if cnt == 0:
            level = 0
        elif cnt >= 8:
            level = 4
        else:
            level = min(4, cnt // 2 + 1)

        data.append({
            'date': date_str,
            'count': cnt,
            'level': level
        })
    return ok(data)
