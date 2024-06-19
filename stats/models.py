import json
from typing import List
import datetime as dt
from datetime import datetime
from collections import defaultdict

from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework import serializers as S
import pytz

from projects.models import Project
from .utils import CustomJSONEncoder


# class GeneralData(models.Model):
#     project = models.ForeignKey(Project, on_delete=models.CASCADE)

#     commits_count = models.IntegerField(default=0)
#     active_days_count = models.IntegerField(default=0)
#     age = models.IntegerField(default=0)
#     files_count = models.IntegerField(default=0)
#     first_commit_id = models.CharField(max_length=50)
#     last_commit_id = models.CharField(max_length=50)
#     first_commit_at = models.DateTimeField()
#     last_commit_at = models.DateTimeField()


# class GeneralDataSerializer(S.ModelSerializer):
#     project_name = S.CharField(source='project.name')
#     # age = S.SerializerMethodField()

#     class Meta:
#         model = GeneralData
#         exclude = ['id', 'project', ]

#     # def get_age(self, obj):
#     #     return obj.age


default_json_list = json.dumps([])
default_json_obj = json.dumps({})

class ActivityData(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    # commit counts in week/month/year
    weekly_activity = models.JSONField(default=list, encoder=DjangoJSONEncoder)
    monthly_activity = models.JSONField(default=list, encoder=DjangoJSONEncoder)
    yearly_activity = models.JSONField(default=list, encoder=DjangoJSONEncoder)

    @property
    def recent_weekly_activity(self):
        # Get the Monday of the current week
        today = datetime.now(tz=dt.timezone.utc)
        this_monday = today - dt.timedelta(days=today.weekday())
        this_monday = this_monday.replace(hour=0, minute=0, second=0, microsecond=0)

        # Calculate the start date for the past 52 weeks
        start_date = this_monday - dt.timedelta(weeks=52)

        data_dict = defaultdict(int)
        # Iterate through the data and add the data to the dictionary
        for item in self.weekly_activity:
            # de-serialize jsondate string
            if isinstance(item['week'], datetime):
                week_date = item['week']
            else:
                week_date = datetime.strptime(item['week'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.utc)

            if start_date <= week_date <= this_monday:
                data_dict[week_date] = item['commit_count']

        print(data_dict)

        past_52_weeks = [this_monday - dt.timedelta(weeks=x) for x in range(52)]

        filtered_data = [
            {'week': week, 'commit_count': data_dict[week]} for week in past_52_weeks[::-1]
        ]

        return filtered_data
    
    # _recent_weekly_activity = models.TextField(default=default_json_list)  # JSON field
    # _month_in_year_activity = models.TextField(default=default_json_obj)  # JSON field
    # _weekday_activity = models.TextField(default=default_json_obj)  # JSON field
    # _hourly_activity = models.TextField(default=default_json_obj)  # JSON field; Note: hour is in local timezone

    # def get_recent_weekly_activity(self):
    #     if self._recent_weekly_activity:
    #         return json.loads(self._recent_weekly_activity)
    #     else:
    #         return {}

    # def set_recent_weekly_activity(self, val: List):
    #     self._recent_weekly_activity = json.dumps(val)

    # recent_weekly_activity = property(get_recent_weekly_activity, set_recent_weekly_activity)

    # def get_month_in_year_activity(self):
    #     if self._month_in_year_activity:
    #         return json.loads(self._month_in_year_activity)
    #     else:
    #         return {}

    # def set_month_in_year_activity(self, val: List):
    #     self._month_in_year_activity = json.dumps(val)

    # month_in_year_activity = property(get_month_in_year_activity, set_month_in_year_activity)

    # def get_weekday_activity(self):
    #     if self._weekday_activity:
    #         return json.loads(self._weekday_activity)
    #     else:
    #         return {}

    # def set_weekday_activity(self, val: List):
    #     self._weekday_activity = json.dumps(val)

    # weekday_activity = property(get_weekday_activity, set_weekday_activity)

    # def get_hourly_activity(self):
    #     if self._hourly_activity:
    #         return json.loads(self._hourly_activity)
    #     else:
    #         return {}

    # def set_hourly_activity(self, val: List):
    #     self._hourly_activity = json.dumps(val)

    # hourly_activity = property(get_hourly_activity, set_hourly_activity)


class ActivityDataSerializer(S.ModelSerializer):
    recent_weekly_activity = S.SerializerMethodField()
    # month_in_year_activity = S.SerializerMethodField()
    # weekday_activity = S.SerializerMethodField()
    # hourly_activity = S.SerializerMethodField()

    class Meta:
        model = ActivityData
        exclude = [
            'id', 'project',
            # 'weekly_activity',
            # '_month_in_year_activity',
            # '_weekday_activity',
            # '_hourly_activity',
        ]

    def get_recent_weekly_activity(self, obj):
        return obj.recent_weekly_activity

    # def get_month_in_year_activity(self, obj):
    #     return obj.month_in_year_activity

    # def get_weekday_activity(self, obj):
    #     return obj.weekday_activity

    # def get_hourly_activity(self, obj):
    #     return obj.hourly_activity


# class AuthorData(models.Model):
#     project = models.ForeignKey(Project, on_delete=models.CASCADE)

#     author_email = models.CharField(max_length=50)
#     author_name = models.CharField(max_length=50)
#     commit_count = models.IntegerField(default=0)
#     first_commit_date = models.DateTimeField()
#     last_commit_date = models.DateTimeField()

#     contributed_days = models.IntegerField()
#     active_days = models.IntegerField()

#     # _authors_statistics = models.TextField(default=default_json_list)  # JSON field

#     # def get_authors_statistics(self):
#     #     if self._authors_statistics:
#     #         return json.loads(self._authors_statistics)
#     #     else:
#     #         return {}

#     # def set_authors_statistics(self, val: List):
#     #     self._authors_statistics = json.dumps(val, cls=CustomJSONEncoder)

#     # authors_statistics = property(get_authors_statistics, set_authors_statistics)


# class AuthorDataSerializer(S.ModelSerializer):
#     project_name = S.CharField(source='project.name')
#     # authors_statistics = S.SerializerMethodField()

#     class Meta:
#         model = AuthorData
#         exclude = [
#             'id', 'project',
#             # '_authors_statistics',
#         ]

#     # def get_authors_statistics(self, obj):
#     #     return obj.authors_statistics


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
