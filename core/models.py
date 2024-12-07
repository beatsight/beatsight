"""
This file is part of Beatsight.

Copyright (C) 2024-2025 Beatsight Ltd.
Licensed under the GNU General Public License v3.0.
"""

from django.db import models
from beatsight.models import TimestampedModel

class TaskLock(TimestampedModel):
    task_name = models.CharField(max_length=255, unique=True)
    acquired_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return self.task_name
