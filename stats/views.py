import json
import sys
from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from django.utils.timezone import get_current_timezone

from projects.models import Project
from repo_sync.models import SyncInfo
from stats.models import GeneralData, GeneralDataSerializer, ActivityData, ActivityDataSerializer, \
    AuthorData, AuthorDataSerializer, FileData, FileDataSerializer

from vendor.repostat.report.jsonreportcreator import JSONReportCreator
from vendor.repostat.tools.configuration import Configuration
from vendor.repostat.analysis.gitrepository import GitRepository


def get_a_project_stat(p: Project, force=False):
    """Get stat data of a project."""

    try:
        si = SyncInfo.objects.get(project=p)
    except SyncInfo.DoesNotExist:
        si = None

    try:
        gd = GeneralData.objects.get(project=p)
    except GeneralData.DoesNotExist:
        gd = None

    try:
        ac = ActivityData.objects.get(project=p)
    except ActivityData.DoesNotExist:
        ac = None

    try:
        au = AuthorData.objects.get(project=p)
    except AuthorData.DoesNotExist:
        au = None

    try:
        fd = FileData.objects.get(project=p)
    except FileData.DoesNotExist:
        fd = None

    if force is False and si and gd and si.head_commit == gd.last_stat_commit:
        # not modified
        gd_s = GeneralDataSerializer(gd)

        if ac:
            ac_s = ActivityDataSerializer(ac)
        else:
            ac_s = None

        au_s = AuthorDataSerializer(au) if au else None
        fd_s = FileDataSerializer(fd) if fd else None
    else:
        # start to generate stat data
        if force is True:
            last_sync_commit = ''
        else:
            last_sync_commit = gd.last_stat_commit if gd else ''
        repo = GitRepository(
            p.repo_path, prev_commit_oid=last_sync_commit)
        config = Configuration([p.repo_path, '.'])
        j_report = JSONReportCreator(config, repo)
        data = j_report.create()

        general_data = data['general']
        if gd is None:
            gd = GeneralData(project=p)
        gd.commits_count += general_data['commits_count']
        gd.active_days_count += general_data['active_days_count']
        gd.files_count = general_data['files_count']
        gd.first_commit_id = general_data['first_commit_id']
        gd.first_commit_date = timezone.make_aware(general_data['first_commit_date'])
        gd.last_commit_id = general_data['last_commit_id']
        gd.last_commit_date = timezone.make_aware(general_data['last_commit_date'])
        gd.save()
        gd_s = GeneralDataSerializer(gd)

        activity_data = data['activity']
        if ac is None:
            ac = ActivityData(project=p)
        ac.recent_weekly_activity = activity_data['recent_weekly_activity']
        ac.month_in_year_activity = activity_data['month_in_year_activity']
        ac.weekday_activity = activity_data['weekday_activity']
        ac.hourly_activity = activity_data['hourly_activity']
        ac.save()
        ac_s = ActivityDataSerializer(ac)

        author_data = data['authors']
        if au is None:
            au = AuthorData(project=p)
        au.top_authors_statistics = author_data['top_authors_statistics']
        au.save()
        au_s = AuthorDataSerializer(au)

        files_data = data['files']
        if fd is None:
            fd = FileData(project=p)
        fd.file_summary = files_data['file_summary']
        fd.total_files_count = files_data['total_files_count']
        fd.total_lines_count = files_data['total_lines_count']
        fd.save()
        fd_s = FileDataSerializer(fd)

        # save current commit as last stat commit
        gd.last_stat_commit = si.head_commit
        gd.save()

    return {
        'general': gd_s.data,
        'activity': ac_s.data if ac_s else {},
        'authors': au_s.data if au_s else {},
        'files': fd_s.data if fd_s else {},
    }


def index(request):
    res = []

    proj = request.GET.get('proj', '')
    force = True if request.GET.get('force', '') == '1' else False

    for p in Project.objects.all():
        if proj and p.name == proj:
            res.append(get_a_project_stat(p, force=force))

    return HttpResponse(json.dumps(res), content_type='application/json')
