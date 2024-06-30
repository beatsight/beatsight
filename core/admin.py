from django.contrib import admin

from .models import TaskLock


class TaskLockAdmin(admin.ModelAdmin):
    list_display = ('id', 'task_name', 'acquired_at', 'expires_at', 'created_at')


admin.site.register(TaskLock, TaskLockAdmin)
