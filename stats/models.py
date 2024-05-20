import json
from typing import List

from django.db import models
from rest_framework import serializers as S

from projects.models import Project


class GeneralData(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    _last_stat_commit = models.CharField(max_length=50, default=None, null=True)

    # accumulated
    commits_count = models.IntegerField(default=0)
    active_days_count = models.IntegerField(default=0)

    # replace
    files_count = models.IntegerField(default=0)
    first_commit_id = models.CharField(max_length=50)
    last_commit_id = models.CharField(max_length=50)
    first_commit_date = models.DateTimeField()
    last_commit_date = models.DateTimeField()

    @property
    def age(self):
        return (self.last_commit_date - self.first_commit_date).days

class GeneralDataSerializer(S.ModelSerializer):
    project_name = S.CharField(source='project.name')
    age = S.SerializerMethodField()

    class Meta:
        model = GeneralData
        exclude = ['id', 'project']

    def get_age(self, obj):
        return obj.age


default_json_list = json.dumps([])
default_json_obj = json.dumps({})

class ActivityData(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    _recent_weekly_activity = models.CharField(max_length=4096, default=default_json_list)  # JSON field
    _month_in_year_activity = models.CharField(max_length=4096, default=default_json_obj)  # JSON field
    _weekday_activity = models.CharField(max_length=4096, default=default_json_obj)  # JSON field
    _hourly_activity = models.CharField(max_length=4096, default=default_json_obj)  # JSON field

    def get_recent_weekly_activity(self):
        if self._recent_weekly_activity:
            return json.loads(self._recent_weekly_activity)
        else:
            return {}

    def set_recent_weekly_activity(self, val: List):
        self._recent_weekly_activity = json.dumps(val)

    recent_weekly_activity = property(get_recent_weekly_activity, set_recent_weekly_activity)

    def get_month_in_year_activity(self):
        if self._month_in_year_activity:
            return json.loads(self._month_in_year_activity)
        else:
            return {}

    def set_month_in_year_activity(self, val: List):
        self._month_in_year_activity = json.dumps(val)

    month_in_year_activity = property(get_month_in_year_activity, set_month_in_year_activity)

    def get_weekday_activity(self):
        if self._weekday_activity:
            return json.loads(self._weekday_activity)
        else:
            return {}

    def set_weekday_activity(self, val: List):
        self._weekday_activity = json.dumps(val)

    weekday_activity = property(get_weekday_activity, set_weekday_activity)

    def get_hourly_activity(self):
        if self._hourly_activity:
            return json.loads(self._hourly_activity)
        else:
            return {}

    def set_hourly_activity(self, val: List):
        self._hourly_activity = json.dumps(val)

    hourly_activity = property(get_hourly_activity, set_hourly_activity)


class ActivityDataSerializer(S.ModelSerializer):
    # project_name = S.CharField(source='project.name')
    recent_weekly_activity = S.SerializerMethodField()
    month_in_year_activity = S.SerializerMethodField()
    weekday_activity = S.SerializerMethodField()
    hourly_activity = S.SerializerMethodField()

    class Meta:
        model = ActivityData
        exclude = [
            'id', 'project',
            '_recent_weekly_activity',
            '_month_in_year_activity',
            '_weekday_activity',
            '_hourly_activity',
        ]

    def get_recent_weekly_activity(self, obj):
        return obj.recent_weekly_activity

    def get_month_in_year_activity(self, obj):
        return obj.month_in_year_activity

    def get_weekday_activity(self, obj):
        return obj.weekday_activity

    def get_hourly_activity(self, obj):
        return obj.hourly_activity
