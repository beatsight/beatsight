import json
import sys
from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponse

from projects.models import Project
from repo_sync.models import SyncInfo
from stats.models import GeneralData, GeneralDataSerializer, ActivityData, ActivityDataSerializer

from vendor.repostat.report.jsonreportcreator import JSONReportCreator
from vendor.repostat.tools.configuration import Configuration
from vendor.repostat.analysis.gitrepository import GitRepository


# # Custom serializer function for datetime
# def datetime_serializer(obj):
#     if isinstance(obj, datetime):
#         return obj.isoformat()
#     else:
#         return obj

def get_a_project_stat(p: Project):
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
        ad = ActivityData.objects.get(project=p)
    except ActivityData.DoesNotExist:
        ad = ActivityData(project=p)

    if si and gd and si.head_commit == gd.last_stat_commit:
        # not modified
        gd_s = GeneralDataSerializer(gd)

        if ad:
            ad_s = ActivityDataSerializer(ad)
    else:
        # start to generate stat data
        last_sync_commit = gd.last_commit_id if gd else ''
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
        gd.first_commit_date = general_data['first_commit_date']
        gd.last_commit_id = general_data['last_commit_id']
        gd.last_commit_date = general_data['last_commit_date']
        gd.save()
        gd_s = GeneralDataSerializer(gd)

        activity_data = data['activity']
        try:
            ad = ActivityData.objects.get(project=p)
        except ActivityData.DoesNotExist:
            ad = ActivityData(project=p)
        ad.recent_weekly_activity = activity_data['recent_weekly_activity']
        ad.month_in_year_activity = activity_data['month_in_year_activity']
        ad.weekday_activity = activity_data['weekday_activity']
        ad.hourly_activity = activity_data['hourly_activity']
        ad.save()
        ad_s = ActivityDataSerializer(ad)
        print(ad_s.data)

        # save current commit as last stat commit
        si.last_stat_commit = gd.last_commit_id
        si.save()

    return {
        'general': gd_s.data,
        'activity': ad_s.data if ad_s else {},
        'authors': {},
        'files': {},
    }


def index(request):
    res = []

    for p in Project.objects.all():
        res.append(get_a_project_stat(p))

    return HttpResponse(json.dumps(res), content_type='application/json')
