import os
import time
import logging

from django.conf import settings
from django.utils import timezone
from celery import shared_task

from projects.models import Project
from developers.models import Developer
from beatsight.consts import CONN_SUCCESS, CONN_ERROR, STATING, STAT_SUCCESS, STAT_ERROR, INIT
from beatsight.utils.task_lock import lock_task, unlock_task
from beatsight.utils.git import full_clone_repo_with_branch, switch_repo_branch, pull_repo_updates
from beatsight import celery_app
from stats.views import get_a_project_stat, calculate_authors_data
from stats.utils import delete_dataframes_from_duckdb

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

    if res is True:
        proj.sync_status = CONN_SUCCESS
        proj.sync_log = ''
        proj.save()
        stat_repo_task.delay(proj_id, True)

@shared_task()
def stat_repo_task(proj_id, force=False):
    logger.debug(f'start stat_repo_task {proj_id}')

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
        get_a_project_stat(proj, force=force)
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

@shared_task()
def cleanup_after_repo_remove_task(proj_name, author_emails):
    logger.debug(f'start cleanup_after_repo_remove_task {proj_name}')

    # TODO: lock daily_commits_db
    daily_commits_db = os.path.join(settings.STAT_DB_DIR, "daily_commits")
    delete_dataframes_from_duckdb("author_daily_commits", f"project='{proj_name}'",
                                  db=daily_commits_db)
    print('calculate_authors_data', author_emails)
    calculate_authors_data(author_emails, daily_commits_db)

    for dev in Developer.objects.filter(email__in=author_emails):
        dev.remove_a_project()
        if dev.total_projects <= 0:
            dev.delete()
            logger.debug(f'delete orphan developer {dev.email}')

    logger.debug(f'finish cleanup_after_repo_remove_task {proj_name}')


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

    for p in Project.objects.exclude(sync_status=INIT):
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
            stat_repo_task.delay(p.id, False)

    logger.debug('end update_repo_task')
    unlock_task(lock)

@shared_task()
def clean_orphan_developers():
    logger.debug('start clean_orphan_developers...')

    for dev in Developer.objects.all():
        if dev.projects.count() == 0:
            dev.delete()
            logger.debug(f'delete orphan developer {dev.email}')

    logger.debug('end clean_orphan_developers')

    
