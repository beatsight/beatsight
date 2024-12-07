"""
This file is part of Beatsight.

Copyright (C) 2024-2025 Beatsight Ltd.
Licensed under the GNU General Public License v3.0.
"""

from django.db import models
from django.utils import timezone

class TimestampedModel(models.Model):
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.created_at:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        return super().save(*args, **kwargs)
