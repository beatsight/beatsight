import json

from django.http import Http404
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions, viewsets
from rest_framework.viewsets import GenericViewSet
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import action

from stats.models import ActivityData
from stats.utils import fetch_from_duckdb
from beatsight.utils import CustomJSONEncoder
from beatsight.utils.response import ok, client_error, server_error
from beatsight.utils.git import test_repo_and_branch, RepoDoesNotExist, BranchDoesNotExist
from developers.models import DeveloperContribution, DeveloperContributionSerializer

from .models import Project, SimpleSerializer, DetailSerializer

class ListCreate(generics.ListCreateAPIView):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Project.objects.all()
    serializer_class = SimpleSerializer
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        res = []
        for p in self.get_queryset():
            try:
                ac = ActivityData.objects.get(project=p)
            except ActivityData.DoesNotExist:
                ac = None
            recent_weekly_activity = ac.recent_weekly_activity if ac else None
            ss = SimpleSerializer(
                p, recent_weekly_activity=recent_weekly_activity
            )
            res.append(ss.data)
        return ok(res)

    def create(self, request):
        req_data = json.loads(request.body)
        repo_url = req_data['repo_url'].strip()
        name = req_data['name'].strip()
        repo_branch = req_data['repo_branch'].strip()

        if not (repo_url.startswith('ssh://') or repo_url.startswith('git@')):
            return client_error('项目地址仅支持 SSH 方式，不支持 HTTP')
        # try:
        #     test_repo_and_branch(repo_url, name, repo_branch)
        # except RepoDoesNotExist:
        #     return client_error('项目地址不存在或无法访问，请检查')
        # except BranchDoesNotExist:
        #     return client_error('项目分支不存，请检查')

        p = Project(name=name, repo_url=repo_url, repo_path='', repo_branch=repo_branch)
        p.save()
        p.refresh_from_db()

        res = SimpleSerializer(p).data
        return Response(res)

class Detail(GenericViewSet):
    queryset = Project.objects.all()
    serializer_class = DetailSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        try:
            obj = Project.objects.get(name=self.kwargs['name'])
        except Project.DoesNotExist:
            raise Http404
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

        req_data = json.loads(request.body)
        p.name = req_data['name'].strip()
        p.repo_url = req_data['repo_url'].strip()
        p.repo_branch = req_data['repo_branch'].strip()
        p.save()
        p.refresh_from_db()

        res = SimpleSerializer(p).data
        return Response(res)

    def destroy(self, request, *args, **kwargs):
        assert False
        p = self.get_object()
        p.delete()
        return Response({})

    @action(detail=True, methods=['get'])
    def contributors(self, request, *args, **kwargs):
        p = self.get_object()
        res = []
        for e in DeveloperContribution.objects.filter(project=p):
            serializer = DeveloperContributionSerializer(e)
            res.append(serializer.data)
            return Response(res)


# #### --------------------
# @csrf_exempt
# def index(request):
#     """list all projects"""
#     if request.method == 'POST':
#         req_data = json.loads(request.body)
#         repo_url = req_data['repo_url'].strip()
#         name = req_data['name'].strip()
#         repo_branch = req_data['repo_branch'].strip()

#         if repo_url.startswith('http://') or repo_url.startswith('https://'):
#             return JsonResponse({'error': '项目地址仅支持 SSH 方式，不支持 HTTP'}, status=400)
#         try:
#             test_repo_and_branch(repo_url, name, repo_branch)
#         except RepoDoesNotExist:
#             return JsonResponse({'error': '项目地址不存在或无法访问，请检查'}, status=400)
#         except BranchDoesNotExist:
#             return JsonResponse({'error': '项目分支不存，请检查'}, status=400)

#         p = Project(name=name, repo_url=repo_url, repo_path='', repo_branch=repo_branch)
#         p.save()
#         p.refresh_from_db()

#         res = SimpleSerializer(p).data
#         return JsonResponse(res, safe=False)

#     # get
#     res = []
#     for p in Project.objects.all():
#         try:
#             ac = ActivityData.objects.get(project=p)
#         except ActivityData.DoesNotExist:
#             ac = None
#         recent_weekly_activity = ac.recent_weekly_activity if ac else None

#         ss = SimpleSerializer(
#             p, recent_weekly_activity=recent_weekly_activity
#         )
#         res.append(ss.data)

#     return JsonResponse(res, safe=False)
#     # return HttpResponse(json.dumps(res, cls=CustomJSONEncoder),
#     #                     content_type='application/json')

# @csrf_exempt
# def detail(request, proj):
#     """get detail of a project (recent activity, top authors ...)"""
#     p = get_object_or_404(Project, name=proj)
#     if request.method == 'DELETE':
#         p.delete()
#         return JsonResponse({})

#     elif request.method == 'POST':
#         req_data = json.loads(request.body)
#         p.name = req_data['name'].strip()
#         p.repo_url = req_data['repo_url'].strip()
#         p.repo_branch = req_data['repo_branch'].strip()
#         p.save()
#         p.refresh_from_db()

#         res = SimpleSerializer(p).data
#         return JsonResponse(res, safe=False)

#     try:
#         ac = ActivityData.objects.get(project=p)
#     except ActivityData.DoesNotExist:
#         ac = None
#     weekly_activity = ac.weekly_activity if ac else None
#     recent_weekly_activity = ac.recent_weekly_activity if ac else None

#     authors = []
#     for e in DeveloperContribution.objects.filter(project=p):
#         authors.append(DeveloperContributionSerializer(e).data)
#     commits_total = sum(e['commits_count'] for e in authors)
#     for e in authors:
#         e['percentage'] = round(e['commits_count'] / commits_total * 100, 1)
#     authors = sorted(authors, key=lambda x: x['commits_count'], reverse=True)

#     s = DetailSerializer(
#         p, weekly_activity=weekly_activity, recent_weekly_activity=recent_weekly_activity,
#         authors_statistics=authors
#     )
#     return JsonResponse(s.data, safe=False)
#     # return HttpResponse(json.dumps(res), content_type='application/json')

# def contributors(request, proj):
#     """get authors' contribution distribution of a project"""
#     p = get_object_or_404(Project, name=proj)

#     res = []
#     for e in DeveloperContribution.objects.filter(project=p):
#         serializer = DeveloperContributionSerializer(e)
#         res.append(serializer.data)

#     return JsonResponse(res, safe=False)
