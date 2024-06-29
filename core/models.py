from django.db import models
from beatsight.models import TimestampedModel

class TaskLock(TimestampedModel):
    task_name = models.CharField(max_length=255, unique=True)
    acquired_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return self.task_name
