"""
This file is part of Beatsight.

Copyright (C) 2024-2025 Beatsight Ltd.
Licensed under the GNU General Public License v3.0.
"""
from collections import defaultdict
import json
import logging
import datetime

import pytz
from django.conf import settings
from django.http import Http404
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext as _
from django.utils.timezone import make_aware, localtime
from rest_framework import permissions, viewsets
from rest_framework.viewsets import GenericViewSet
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from stats.models import ActivityData
from beatsight.utils import CustomJSONEncoder
from beatsight.utils.response import ok, client_error, server_error
from beatsight.pagination import CustomPagination
from beatsight.utils.git import test_repo_and_branch, RepoDoesNotExist, BranchDoesNotExist, update_remote_url
from developers.models import DeveloperContribution, DeveloperContributionSerializer
from developers.utils import calculate_calendar_level

from .models import Project, SimpleSerializer, DetailSerializer, ProjectActivity, ProjectActivitySerializer
from .tasks import init_repo_task, switch_repo_branch_task, cleanup_after_repo_remove_task, force_update_one_repo_task

logger = logging.getLogger(settings.LOGNAME)

def clean_project_fields(req_data, test_conn=False):
    req_data['repo_url'] = req_data['repo_url'].strip()
    req_data['name'] = req_data['name'].strip()
    req_data['repo_branch'] = req_data['repo_branch'].strip()

    repo_url = req_data['repo_url']
    name = req_data['name']
    repo_branch = req_data['repo_branch']

    if not (repo_url.startswith('ssh://') or repo_url.startswith('git@')):
        return False, _('The project address only supports SSH protocol.')

    if test_conn:
        try:
            test_repo_and_branch(repo_url, name, repo_branch)
        except RepoDoesNotExist:
            return False, _('The provided project address cannot be found or reached. Please verify the address and try again.')
        except BranchDoesNotExist:
            return False, _('The specified project branch could not be found. Please verify the branch name and try again.')
    return True, req_data

class ListCreate(generics.ListCreateAPIView):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Project.objects.all()
    serializer_class = SimpleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()

        query = self.request.GET.get('query', '')
        if query:               # TODO: performance issue!
            qs = super().get_queryset().filter(
                Q(name__contains=query) |
                Q(repo_url__contains=query)
            )

        sort_by = self.request.GET.get('sortBy', '')
        if sort_by:
            order = self.request.GET.get('order', 'asc')
            if order == 'desc':
                qs = qs.order_by(f'-{sort_by}')
            else:
                qs = qs.order_by(sort_by)
        else:
            qs = qs.order_by('-created_at')

        return qs

    def list(self, request):
        query_fields = request.GET.get('fields', '')

        if query_fields:
            fields = [e.strip() for e in query_fields.split(',')]
            qs = self.get_queryset().values(*fields)
            return ok(list(qs))

        qs = self.get_queryset()
        pnp = CustomPagination()
        page = pnp.paginate_queryset(qs, request)

        res = []
        for p in page:
            # try:
            #     ac = ActivityData.objects.get(project=p)
            # except ActivityData.DoesNotExist:
            #     ac = None
            # recent_weekly_activity = ac.recent_weekly_activity if ac else None
            ss = SimpleSerializer(
                p, recent_weekly_activity=None
            )
            res.append(ss.data)

        return pnp.get_paginated_response(res)

    def create(self, request):
        if not request.user.is_staff:
            return client_error(_("Only admins can create projects."))

        req_data = request.data
        test_conn = True if req_data.get('test_conn', 0) == 1 else False

        ok, ret = clean_project_fields(req_data, test_conn)
        if not ok:
            err = ret
            return client_error(err)
        if test_conn:
            return Response({})

        data = ret

        name, repo_url, repo_branch = data['name'], data['repo_url'], data['repo_branch']
        if Project.objects.filter(name=name).count() > 0:
            return client_error(_('A project with that name already exists. Please verify the name and try again.'))

        p = Project(name=name, repo_url=repo_url, repo_branch=repo_branch)
        p.save()
        p.refresh_from_db()

        init_repo_task.delay(p.id, repo_url, name, repo_branch)

        res = SimpleSerializer(p).data
        return Response(res)

class Detail(GenericViewSet):
    queryset = Project.objects.all()
    serializer_class = DetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            obj = Project.objects.get(name=self.kwargs['name'])
        except Project.DoesNotExist:
            raise Http404(f"Project（{self.kwargs['name']}）does not exist")
        return obj

    def retrieve(self, request, *args, **kwargs):
        p = self.get_object()
        try:
            ac = ActivityData.objects.get(project=p)
        except ActivityData.DoesNotExist:
            ac = None
        weekly_activity = ac.weekly_activity if ac else None
        recent_weekly_activity = ac.recent_weekly_activity if ac else None

        authors = []
        for e in DeveloperContribution.objects.filter(project=p):
            authors.append(DeveloperContributionSerializer(e).data)
        commits_total = sum(e['commits_count'] for e in authors)
        for e in authors:
            e['percentage'] = round(e['commits_count'] / commits_total * 100, 1)
        authors = sorted(authors, key=lambda x: x['commits_count'], reverse=True)

        s = DetailSerializer(
            p, weekly_activity=weekly_activity, recent_weekly_activity=recent_weekly_activity,
            authors_statistics=authors
        )
        return Response(s.data)

    def update(self, request, *args, **kwargs):
        p = self.get_object()

        if not request.user.is_staff:
            return client_error(_("Only admins can update projects."))

        req_data = json.loads(request.body)
        test_conn = True if req_data.get('test_conn', 0) == 1 else False

        # ok, ret = clean_project_fields(req_data, test_conn)
        # if not ok:
        #     err = ret
        #     return client_error(err)
        # if test_conn:
        #     return Response({})

        data = req_data

        # old_url = p.repo_url
        old_branch = p.repo_branch

        save_obj = False
        if 'desc' in data:
            p.desc = data['desc'].strip()
            save_obj = True
        if 'repo_branch' in data:
            p.repo_branch = data['repo_branch'].strip()
            save_obj = True
        if 'ignore_list' in data:
            p.ignore_list = data['ignore_list'].strip()
            save_obj = True

        if save_obj:
            p.save()
            p.refresh_from_db()

        # if p.repo_url != old_url:
        #     update_remote_url(p.repo_path, p.repo_url)

        if p.repo_branch != old_branch:
            switch_repo_branch_task.delay(p.id, p.repo_branch)

        if 're_stat' in data and data['re_stat'] is True:
            force_update_one_repo_task.delay(p.id)

        res = SimpleSerializer(p).data
        return Response(res)

    def destroy(self, request, *args, **kwargs):
        p = self.get_object()

        if not request.user.is_staff:
            return client_error(_("Only admins can delete projects."))

        proj_name = p.name
        author_emails = [dev.email for dev in p.developer_set.all()]

        p.delete()

        # re-calculate authors' activities, most used languages, contributions ... in that project
        cleanup_after_repo_remove_task.delay(proj_name, author_emails)

        return Response({})

    @action(detail=True, methods=['get'])
    def contributors(self, request, *args, **kwargs):
        p = self.get_object()
        res = []
        for e in DeveloperContribution.objects.filter(project=p):
            serializer = DeveloperContributionSerializer(e)
            res.append(serializer.data)
            return Response(res)

    @action(detail=True, methods=['get'])
    def contrib_calendar(self, request, *args, **kwargs):
        p = self.get_object()

        year = request.GET.get('year')
        if not year:
            # TODO: use util function
            native_end_dt = datetime.datetime.now()
            native_start_dt = native_end_dt - datetime.timedelta(days=366)
        else:
            year = int(year)
            native_start_dt = datetime.datetime(year, 1, 1, hour=0, minute=0, second=0, microsecond=0)
            native_end_dt = datetime.datetime(year, 12, 31, hour=23, minute=59, second=59, microsecond=999999)

        start_date = make_aware(native_start_dt, timezone=pytz.timezone(settings.TIME_ZONE))
        end_date = make_aware(native_end_dt, timezone=pytz.timezone(settings.TIME_ZONE))

        res = {}
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            res[date_str] = []
            current_date += datetime.timedelta(days=1)

        for e in ProjectActivity.objects.filter(
                project=p,
                author_datetime__gte=start_date,
                author_datetime__lt=end_date + datetime.timedelta(days=1)
        ):
            date_str = localtime(e.author_datetime).strftime('%Y-%m-%d')
            if date_str not in res:
                continue
            res[date_str].append(e.commit_sha)

        data = []
        for date_str, val in res.items():
            cnt = len(val)
            level = calculate_calendar_level(cnt, 2)

            data.append({
                'date': date_str,
                'count': cnt,
                'level': level
            })
        return ok(data)

    @action(detail=True, methods=['get'])
    def activities(self, request, *args, **kwargs):
        p = self.get_object()

        qs = ProjectActivity.objects.filter(project=p).order_by(
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
        s = ProjectActivitySerializer(page, many=True)
     
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
        

class ActivityList(generics.ListAPIView):
    queryset = ProjectActivity.objects.all()
    serializer_class = ProjectActivitySerializer
    # pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()

        start_date_str = self.request.GET.get('startDate')
        end_date_str = self.request.GET.get('endDate')
        if start_date_str and end_date_str:
            native_dt = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
            native_start_dt = native_dt.replace(hour=0, minute=0, second=0, microsecond=0)
            native_dt = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')
            native_end_dt = native_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
            start_date = make_aware(native_start_dt, timezone=pytz.timezone(settings.TIME_ZONE))
            end_date = make_aware(native_end_dt, timezone=pytz.timezone(settings.TIME_ZONE))
            qs = qs.filter(author_datetime__gt=start_date, author_datetime__lt=end_date)

        qs = qs.order_by('-author_datetime')
        return qs
