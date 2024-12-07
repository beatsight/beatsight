"""
This file is part of Beatsight.

Copyright (C) 2024-2025 Beatsight Ltd.
Licensed under the GNU General Public License v3.0.
"""

from datetime import timedelta
from django.db import transaction
from django.utils import timezone

from core.models import TaskLock

def lock_task(task_name, lock_duration=timedelta(minutes=30)):
    """
    Acquire a lock for the given task name.
    Returns True if the lock was acquired, False otherwise.
    """
    expires_at = timezone.now() + lock_duration
    try:
        with transaction.atomic():
            lock, created = TaskLock.objects.get_or_create(
                task_name=task_name,
                defaults={'expires_at': expires_at}
            )
            if created or lock.expires_at < timezone.now():
                lock.expires_at = expires_at
                lock.save()
                return True
    except:
        pass
    return False

def unlock_task(task_name):
    """
    Release the lock for the given task name.
    """
    TaskLock.objects.filter(task_name=task_name).delete()
