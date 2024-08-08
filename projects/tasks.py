import time
import logging

from django.conf import settings
from django.utils import timezone
from celery import shared_task

from projects.models import Project
from beatsight.consts import CONN_SUCCESS, CONN_ERROR, STATING, STAT_SUCCESS, STAT_ERROR
from beatsight.utils.task_lock import lock_task, unlock_task
from beatsight.utils.git import full_clone_repo_with_branch, switch_repo_branch, pull_repo_updates
from beatsight import celery_app
from stats.views import get_a_project_stat

logger = logging.getLogger('tasks')

# @celery_app.task
# def test_task(a, b):
#     time.sleep(5)
#     return a + b

@shared_task()
def init_repo_task(proj_id, repo_url, name, repo_branch):
    logger.debug(f'init_repo_task {proj_id} {repo_url} {repo_branch}')

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

        stat_repo_task.delay(proj_id, True)
    except Exception as e:
        proj.sync_status = CONN_ERROR
        proj.sync_log = f'项目地址无法访问或者分支不存在，错误日志：{e}'
        proj.save()

@shared_task()
def switch_repo_branch_task(proj_id, repo_branch):
    try:
        proj = Project.objects.get(id=proj_id)
    except Project.DoesNotExist:
        return

    logger.debug(f'switch repo branch to {repo_branch} - {proj.repo_path}')

    err_msg, res = switch_repo_branch(proj.repo_path, repo_branch)
    if err_msg:
        proj.sync_status = CONN_ERROR
        proj.sync_log = f'项目地址无法访问或者分支不存在，错误日志：{e}'
        proj.save()
        return

    if res is True
        proj.sync_status = CONN_SUCCESS
        proj.sync_log = ''
        proj.save()
        stat_repo_task.delay(proj_id, True)

@shared_task()
def stat_repo_task(proj_id, force=False):
    logger.debug(f'stat_repo_task {proj_id}')

    lock = f'stat_repo_task_#{proj_id}'
    if not lock_task(lock):
        logger.warn(f'stat_repo_task {proj_id} is running, skip')
        return

    try:
        proj = Project.objects.get(id=proj_id)
        proj.sync_status = STATING
        proj.save()
    except Project.DoesNotExist:
        return

    try:
        get_a_project_stat(proj, force=True)
        proj.sync_status = STAT_SUCCESS
        proj.sync_log = ''
        proj.save()
        logging.info(f'finish stat_repo_task {proj_id}')
    except Exception as e:
        proj.sync_status = STAT_ERROR
        proj.sync_log = f'统计失败，错误日志：{e}'
        proj.save()
        logger.error(f'error in stat_repo_task project: {proj.name}-{proj_id}')
        logger.exception(e)
    finally:
        unlock_task(lock)

# from django_celery_beat.decorators import periodic_task
# @periodic_task(run_every=timedelta(seconds=30), name='update_repo_task')
# @singleton

@shared_task()
def update_repo_task():
    logger.debug('start update_repo_task...')

    lock = 'update_repo_task'
    if not lock_task(lock):
        logger.warn('update_repo_task is running, skip')
        return

    for p in Project.objects.filter(sync_status=STAT_SUCCESS):
        err_msg, res = pull_repo_updates(p.repo_path, p.repo_branch)
        if err_msg:
            p.sync_status = CONN_ERROR
            p.sync_log = f'项目地址无法访问或者分支不存在，错误日志：{err_msg}'
            p.save()
            continue

        if res is True:
            logger.info(f'{p.id} - {p.name} has new updates, start stat task')
            p.last_sync_at = timezone.now()
            p.sync_status = STATING
            p.save()
            stat_repo_task.delay(p.id)

    logger.debug('end update_repo_task')
    unlock_task(lock)
