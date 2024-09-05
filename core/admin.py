from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import TaskLock


class TaskLockAdmin(ModelAdmin):
    list_display = ('id', 'task_name', 'acquired_at', 'expires_at', 'created_at')


admin.site.register(TaskLock, TaskLockAdmin)


# ----------
# Note: Registered admin models coming from third party packages are not going to
# properly work with Unfold because of parent class.
# ref: https://unfoldadmin.com/docs/installation/

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group
from django.contrib.sites.admin import SiteAdmin as BaseSiteAdmin
from django.contrib.sites.models import Site

admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.unregister(Site)

@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    pass

@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass

@admin.register(Site)
class SiteAdmin(BaseSiteAdmin, ModelAdmin):
    pass


from django_celery_beat.admin import PeriodicTaskAdmin as BasePeriodicTaskAdmin
from django_celery_beat.admin import ClockedScheduleAdmin as _ClockedScheduleAdmin
from django_celery_beat.admin import CrontabScheduleAdmin as _CrontabScheduleAdmin
from django_celery_beat.models import (
    ClockedSchedule, CrontabSchedule, IntervalSchedule,
    PeriodicTask, PeriodicTasks, SolarSchedule
)

admin.site.unregister(PeriodicTask)
admin.site.unregister(ClockedSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(SolarSchedule)

@admin.register(PeriodicTask)
class PeriodicTaskAdmin(BasePeriodicTaskAdmin, ModelAdmin):
    ...

@admin.register(ClockedSchedule)
class ClockedScheduleAdmin(_ClockedScheduleAdmin, ModelAdmin):
    ...

@admin.register(CrontabSchedule)
class CrontabScheduleAdmin(_CrontabScheduleAdmin, ModelAdmin):
    ...


class IntervalScheduleAdmin(ModelAdmin):
    ...
admin.site.register(IntervalSchedule, IntervalScheduleAdmin)


class SolarScheduleAdmin(ModelAdmin):
    ...
admin.site.register(SolarSchedule, SolarScheduleAdmin)
