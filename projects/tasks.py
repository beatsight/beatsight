import os
import time
import logging

from django.conf import settings
from celery import shared_task

from projects.models import Project
from developers.models import Developer
from beatsight.consts import INIT
from beatsight.utils.task_lock import lock_task, unlock_task
from beatsight.utils.git import full_clone_repo_with_branch, switch_repo_branch, pull_repo_updates, rename_current_branch
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
        proj.sync_success()
        proj.save()

        stat_repo_task.delay(proj_id, True)
    except Exception as e:
        proj.sync_error(f'项目地址无法访问或者分支不存在，错误日志：{e}')
        proj.save()

@shared_task()
def switch_repo_branch_task(proj_id, repo_branch):
    logger.debug(f'project:{proj_id} switch repo branch to {repo_branch}')

    try:
        proj = Project.objects.get(id=proj_id)
    except Project.DoesNotExist:
        return

    err_msg, res = switch_repo_branch(proj.repo_path, repo_branch)
    proj.refresh_from_db()
    if err_msg:
        proj.sync_error(f'项目地址无法访问或者分支不存在，错误日志：{err_msg}')
        proj.save()
        return

    if res is True:
        proj.sync_success()
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
    except Project.DoesNotExist:
        return

    if not proj.is_stating():
        proj.start_stat()
        proj.save()

    log = ''
    try:
        get_a_project_stat(proj, force=force)  # may take a while
        logger.info(f'finish stat_repo_task {proj_id}')
    except Exception as e:
        log = f'统计失败，错误日志：{e}'
        logger.error(f'error in stat_repo_task project: {proj.name}-{proj_id}')
        logger.exception(e)
    finally:
        unlock_task(lock)

    proj = Project.objects.get(id=proj_id)
    if log:
        proj.stat_error(log)
    else:
        proj.stat_success()
    proj.save()

@shared_task()
def force_update_one_repo_task(proj_id):
    logger.debug(f'start force_update_one_repo_task, proj_id: {proj_id}...')

    try:
        p = Project.objects.get(id=proj_id)
    except Project.DoesNotExist:
        return

    p.start_stat()
    p.save()

    if not os.path.exists(p.repo_path):  # 初始化时异常，导致未获取到项目，需要重新获取
        name = f"{proj_id}-{p.name}"
        local_path = full_clone_repo_with_branch(p.repo_url, name, p.repo_branch)
        p.refresh_from_db()
        p.repo_path = local_path
        p.sync_success()
        p.save()
        stat_repo_task.delay(proj_id, True)
    else:
        err_msg, res = rename_current_branch(p.repo_path)
        if err_msg:
            p.refresh_from_db()
            p.sync_error(f'更新失败，错误日志：{err_msg}')
            p.save()
            return
        switch_repo_branch_task.delay(p.id, p.repo_branch)

        # err_msg, res = pull_repo_updates(p.repo_path, p.repo_branch)
        # if err_msg:
        #     logger.debug(f'force_update_one_repo_task got error during pull_repo_updates: {err_msg}')
        #     p.sync_error(f'项目地址无法访问或者分支不存在，错误日志：{err_msg}')
        #     p.save()
        #     return
        # else:
        #     p.sync_success()
        #     p.save()
        #     stat_repo_task.delay(p.id, True)

    logger.debug('end force_update_one_repo_task')

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
            p.sync_error(f'项目地址无法访问或者分支不存在，错误日志：{err_msg}')
            p.save()
            continue
        else:
            p.sync_success()
            p.save()

        if res is True:
            logger.info(f'{p.id} - {p.name} has new updates, start stat task')
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
