import json
from typing import List

from django.db import models
from rest_framework import serializers as S

from projects.models import Project
from .utils import CustomJSONEncoder


class GeneralData(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    last_stat_commit = models.CharField(max_length=50, default=None, null=True)

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
        exclude = ['id', 'project', 'last_stat_commit']

    def get_age(self, obj):
        return obj.age


default_json_list = json.dumps([])
default_json_obj = json.dumps({})

class ActivityData(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    _recent_weekly_activity = models.TextField(default=default_json_list)  # JSON field
    _month_in_year_activity = models.TextField(default=default_json_obj)  # JSON field
    _weekday_activity = models.TextField(default=default_json_obj)  # JSON field
    _hourly_activity = models.TextField(default=default_json_obj)  # JSON field; Note: hour is in local timezone

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


class AuthorData(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    _top_authors_statistics = models.TextField(default=default_json_list)  # JSON field

    def get_top_authors_statistics(self):
        if self._top_authors_statistics:
            return json.loads(self._top_authors_statistics)
        else:
            return {}

    def set_top_authors_statistics(self, val: List):
        self._top_authors_statistics = json.dumps(val, cls=CustomJSONEncoder)

    top_authors_statistics = property(get_top_authors_statistics, set_top_authors_statistics)


class AuthorDataSerializer(S.ModelSerializer):
    top_authors_statistics = S.SerializerMethodField()

    class Meta:
        model = AuthorData
        exclude = [
            'id', 'project',
            '_top_authors_statistics',
        ]

    def get_top_authors_statistics(self, obj):
        return obj.top_authors_statistics


class FileData(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    total_files_count = models.IntegerField(default=0)
    total_lines_count = models.IntegerField(default=0)
    _file_summary = models.TextField(default=default_json_list)  # JSON field

    def get_file_summary(self):
        if self._file_summary:
            return json.loads(self._file_summary)
        else:
            return {}

    def set_file_summary(self, val: List):
        self._file_summary = json.dumps(val, cls=CustomJSONEncoder)

    file_summary = property(get_file_summary, set_file_summary)


class FileDataSerializer(S.ModelSerializer):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    file_summary = S.SerializerMethodField()

    class Meta:
        model = FileData
        exclude = [
            'id', 'project',
            '_file_summary',
        ]

    def get_file_summary(self, obj):
        return obj.file_summary
