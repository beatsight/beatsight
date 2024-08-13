from collections import defaultdict
import datetime

import pytz
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, Http404
from django.utils import timezone
from django.utils.timezone import make_aware
from django.conf import settings
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view

from beatsight.pagination import CustomPagination
from projects.models import SimpleSerializer as ProjectSimpleSerializer
from projects.models import ProjectActiviy, ProjectActiviySerializer
from beatsight.pagination import CustomPagination
from beatsight.utils.response import ok
from beatsight.consts import ACTIVE

from .models import Developer, SimpleSerializer, DetailSerializer, DeveloperContribution, DeveloperContributionSerializer


def index(request):
    """list all developers"""
    res = []
    for e in Developer.objects.all().order_by('rank_percentile')[:100]:
        res.append(SimpleSerializer(e).data)

    return JsonResponse(res, safe=False)

class ListCreate(generics.ListCreateAPIView):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Developer.objects.all()
    serializer_class = SimpleSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        qs = super().get_queryset()

        query = self.request.GET.get('query', '')
        if query:               # TODO: performance issue!
            qs = super().get_queryset().filter(
                Q(email__contains=query) |
                Q(name__contains=query)
            )

        return qs.order_by('email')

def get_obj(email):
    try:
        d = Developer.objects.get(email=email)
    except Developer.DoesNotExist:
        raise Http404(f"开发人员（{email}）不存在")
    return d

@api_view(['GET'])
def detail(request, email):
    """get detail of a developer (recent activity, top projects ...)"""
    d = get_obj(email)

    res = DetailSerializer(d).data

    commits_total = sum(e['commits_count'] for e in res['contribution'])

    for e in res['contribution']:
        e['percentage'] = round(e['commits_count'] / commits_total * 100, 1)

    return ok(res)

def contributions(request, email):
    """get projects' contribution distribution of a developer"""
    d = get_obj(email)

    res = []
    for e in DeveloperContribution.objects.filter(developer=d):
        serializer = DeveloperContributionSerializer(e)
        res.append(serializer.data)

    return JsonResponse(res, safe=False)

@api_view(['GET'])
def activities(request, email):
    d = get_obj(email)

    qs = ProjectActiviy.objects.filter(author_email=email).order_by(
        '-author_datetime'
    )

    start_date, end_date = None, None
    date = request.GET.get('date')
    if date:
        native_dt = datetime.datetime.strptime(date, '%Y-%m-%d')
        native_start_dt = native_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        native_end_dt = native_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
        start_date = make_aware(native_start_dt, timezone=pytz.timezone(settings.TIME_ZONE))
        end_date = make_aware(native_end_dt, timezone=pytz.timezone(settings.TIME_ZONE))

    year = request.GET.get('year')
    if year:
        year = int(year)
        native_start_dt = datetime.datetime(year, 1, 1, hour=0, minute=0, second=0, microsecond=0)
        native_end_dt = datetime.datetime(year, 12, 31, hour=23, minute=59, second=59, microsecond=999999)
        start_date = make_aware(native_start_dt, timezone=pytz.timezone(settings.TIME_ZONE))
        end_date = make_aware(native_end_dt, timezone=pytz.timezone(settings.TIME_ZONE))

    if start_date and end_date:
        qs = qs.filter(author_datetime__gt=start_date, author_datetime__lt=end_date)

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
    d = get_obj(email)

    year = request.GET.get('year')
    if not year:
        end_date = timezone.now().date()
        start_date = end_date - datetime.timedelta(days=366)
    else:
         year = int(year)
         start_date = datetime.date(year, 1, 1)
         end_date = datetime.date(year, 12, 31)

    res = {}
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        res[date_str] = []
        current_date += datetime.timedelta(days=1)

    for e in ProjectActiviy.objects.filter(
            author_email=email,
            author_datetime__gte=start_date,
            author_datetime__lt=end_date + datetime.timedelta(days=1)
    ):
        date_str = e.author_datetime.strftime('%Y-%m-%d')
        res[date_str].append(e.commit_sha)

    data = []
    for date_str, val in res.items():
        cnt = len(val)
        level = 4

        if cnt == 0:
            level = 0
        if cnt >= 1 and cnt < 3:
            level = 1
        if cnt >=3 and cnt < 6:
            level = 2
        if cnt >= 6 and cnt < 9:
            level = 3

        data.append({
            'date': date_str,
            'count': cnt,
            'level': level
        })
    return ok(data)
