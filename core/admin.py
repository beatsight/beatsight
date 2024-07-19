from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import TaskLock


class TaskLockAdmin(ModelAdmin):
    list_display = ('id', 'task_name', 'acquired_at', 'expires_at', 'created_at')


admin.site.register(TaskLock, TaskLockAdmin)
