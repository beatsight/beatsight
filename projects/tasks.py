import time
import logging

from django.conf import settings
from django.utils import timezone
from celery import shared_task

from projects.models import Project
from beatsight.consts import CONN_SUCCESS, CONN_ERROR, STATING, STAT_SUCCESS, STAT_ERROR
from beatsight.utils.git import full_clone_repo_with_branch, switch_repo_branch, pull_repo_updates
from beatsight import celery_app
from stats.views import get_a_project_stat

logger = logging.getLogger(settings.LOGNAME)

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

    logger.info(f'switch repo branch to {repo_branch} - {proj.repo_path}')

    try:
        switch_repo_branch(proj.repo_path, repo_branch)
        proj.sync_status = CONN_SUCCESS
        proj.save()

        stat_repo_task.delay(proj_id)
    except Exception as e:
        logger.error(e)
        proj.sync_status = CONN_ERROR
        proj.save()

@shared_task()
def stat_repo_task(proj_id):
    logging.info(f'stat_repo_task {proj_id}')
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
        logging.info(f'finish stat_repo_task {proj_id}')
    except Exception as e:
        print(e)
        proj.sync_status = STAT_ERROR
        proj.save()
        logging.error(f'error in stat_repo_task {proj_id}')

# from django_celery_beat.decorators import periodic_task
# @periodic_task(run_every=timedelta(seconds=30), name='update_repo_task')
# @singleton

@shared_task()
def update_repo_task():
    logging.info('start update_repo_task...')
    for p in Project.objects.filter(sync_status=STAT_SUCCESS):
        logging.info(f'checking {p.id} - {p.name}...')

        try:
            if pull_repo_updates(p.repo_path, p.repo_branch) is True:
                print('{p.id} - {p.name} has new updates, start stat task')
                stat_repo_task.delay(p.id)
        except Exception as e:
            logging.error(e)
            continue
    logging.info('end update_repo_task')
