import time

from django.utils import timezone
from celery import shared_task

from projects.models import Project
from beatsight.consts import CONN_SUCCESS, CONN_ERROR, STATING, STAT_SUCCESS, STAT_ERROR
from beatsight.utils.git import full_clone_repo_with_branch, switch_repo_branch
from beatsight import celery_app
from stats.views import get_a_project_stat

@celery_app.task
def test_task(a, b):
    time.sleep(5)
    return a + b

@shared_task()
def init_repo_task(proj_id, repo_url, name, repo_branch):
    try:
        proj = Project.objects.get(id=proj_id)
    except Project.DoesNotExist:
        return

    name = f"{proj_id}-{name}"
    try:
        local_path = full_clone_repo_with_branch(repo_url, name, repo_branch)
        proj.repo_path = local_path
        proj.sync_status = CONN_SUCCESS
        proj.last_sync_at = timezone.now()
        proj.save()

        stat_repo_task.delay(proj_id)
    except Exception as e:
        print(e)
        proj.sync_status = CONN_ERROR
        proj.save()

@shared_task()
def switch_repo_branch_task(proj_id, repo_branch):
    try:
        proj = Project.objects.get(id=proj_id)
    except Project.DoesNotExist:
        return

    print(f'switch repo branch to {repo_branch} - {proj.repo_path}')
    switch_repo_branch(proj.repo_path, repo_branch)
    stat_repo_task.delay(proj_id)

@shared_task()
def stat_repo_task(proj_id):
    try:
        proj = Project.objects.get(id=proj_id)
        proj.sync_status = STATING
        proj.save()
    except Project.DoesNotExist:
        return

    try:
        get_a_project_stat(proj, force=True)
        proj.sync_status = STAT_SUCCESS
        proj.save()
    except Exception as e:
        print(e)
        proj.sync_status = STAT_ERROR
        proj.save()
