from django.contrib import admin

from .models import TaskLock


class TaskLockAdmin(admin.ModelAdmin):
    pass


admin.site.register(TaskLock, TaskLockAdmin)
