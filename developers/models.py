"""
This file is part of Beatsight.

Copyright (C) 2024-2025 Beatsight Ltd.
Licensed under the GNU General Public License v3.0.
"""

import random

from django.db import models
import datetime as dt
from datetime import datetime, date
from collections import defaultdict

from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers as S
import pytz

from beatsight.models import TimestampedModel
from projects.models import Project, Language, LanguageSerializer
from projects.models import SimpleSerializer as ProjectSimpleSerializer
from beatsight.consts import ACTIVE, INACTIVE
from beatsight.utils.pl_color import PL_COLOR

from .utils import calculate_rank


class Developer(TimestampedModel):
    DEV_STATUS = (
        (ACTIVE, _('Active')),
        (INACTIVE, _('Inactive'))
    )
    
    name = models.CharField(max_length=200, db_index=True)
    email = models.CharField(max_length=200, unique=True)
    projects = models.ManyToManyField(Project)
    status = models.CharField(max_length=10, choices=DEV_STATUS, default=INACTIVE, db_index=True)

    first_commit_at = models.DateTimeField()
    last_commit_at = models.DateTimeField(db_index=True)
    contributed_days = models.IntegerField(default=0)
    active_days = models.IntegerField(default=0)  # days that have code commits
    active_days_ratio = models.FloatField(default=0)

    total_commits = models.IntegerField(default=0)
    total_insertions = models.IntegerField(default=0)
    total_deletions = models.IntegerField(default=0)

    total_projects = models.IntegerField(default=0, db_index=True)

    rank_level = models.CharField(max_length=10, default='-')
    rank_percentile = models.FloatField(default=0.0, db_index=True)

    def __str__(self):
        return f"{self.name} - {self.email}"

    def save(self, *args, **kwargs):
        if (timezone.now() - self.last_commit_at).days > 90:
            self.status = "inactive"
        else:
            self.status = "active"
        self.contributed_days = (self.last_commit_at - self.first_commit_at).days + 1
        self.active_days_ratio = 0 if self.contributed_days == 0 else self.active_days / self.contributed_days

        return super().save(*args, **kwargs)

    def set_first_last_commit_at(self, first_dt, last_dt):
        if self.first_commit_at is None:
            self.first_commit_at = first_dt

        if first_dt < self.first_commit_at:
            self.first_commit_at = first_dt

        if self.last_commit_at is None:
            self.last_commit_at = last_dt

        if last_dt > self.last_commit_at:
            self.last_commit_at = last_dt

    def add_a_project(self, p):
        self.projects.add(p)
        self.total_projects = len(self.projects.all())
        self.save()

    def remove_a_project(self):
        self.total_projects = len(self.projects.all())
        self.save()
        
    def calculate_rank(self):
        level, percentile = calculate_rank(self.total_commits, self.total_projects,
                                           self.active_days_ratio,
                                           self.total_insertions + self.total_deletions)
        self.rank_level = level
        self.rank_percentile = percentile
        self.save()

    @property
    def recent_weekly_activity(self):
        dev_ac = DeveloperActivity.objects.get(developer=self)
        if dev_ac is None:
            # TODO: add warning
            return []

        # Get the Monday of the current week
        today = datetime.now(tz=dt.timezone.utc)
        this_monday = today - dt.timedelta(days=today.weekday())
        this_monday = this_monday.replace(hour=0, minute=0, second=0, microsecond=0)

        # Calculate the start date for the past 52 weeks
        start_date = this_monday - dt.timedelta(weeks=52)

        data_dict = defaultdict(int)
        # Iterate through the data and add the data to the dictionary
        for item in dev_ac.weekly_activity:
            # de-serialize jsondate string
            if isinstance(item['week'], datetime):
                week_date = item['week']
            else:
                week_date = datetime.strptime(item['week'], '%Y-%m-%d').replace(tzinfo=pytz.utc)

            if start_date <= week_date <= this_monday:
                data_dict[week_date] = item['commit_count']

        past_52_weeks = [this_monday - dt.timedelta(weeks=x) for x in range(52)]
        filtered_data = [
            {'week': week, 'commit_count': data_dict[week]} for week in past_52_weeks[::-1]
        ]

        return filtered_data

class DeveloperActivity(TimestampedModel):
    developer = models.OneToOneField(Developer, on_delete=models.CASCADE, primary_key=True)

    # commit counts in day/week
    daily_activity = models.JSONField(default=list, encoder=DjangoJSONEncoder)
    weekly_activity = models.JSONField(default=list, encoder=DjangoJSONEncoder)

    def __str__(self):
        return f"{self.developer.name}"


class DeveloperLanguage(TimestampedModel):
    developer = models.ForeignKey(Developer, on_delete=models.CASCADE)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    use_count = models.IntegerField()

    def __str__(self):
        return f"{self.developer.name} - {self.language.name}"


class DeveloperContribution(TimestampedModel):
    developer = models.ForeignKey(Developer, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    daily_contribution = models.JSONField(default=list, encoder=DjangoJSONEncoder)
    commits_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.developer.name} - {self.project.name}"


########## serializers


class DeveloperActivitySerializer(S.ModelSerializer):
    class Meta:
        model = DeveloperActivity
        fields = ['daily_activity', 'weekly_activity']

class DeveloperLanguageSerializer(S.ModelSerializer):
    # language = LanguageSerializer(read_only=True)
    language_name = S.ReadOnlyField(source='language.name')
    language_color = S.SerializerMethodField()

    class Meta:
        model = DeveloperLanguage
        fields = ['language_name', 'language_color', 'use_count']

    def get_language_color(self, obj):
        d = PL_COLOR.get(obj.language.name)
        if not d:
            red = random.randint(0, 255)
            green = random.randint(0, 255)
            blue = random.randint(0, 255)
            return red, green, blue
        return d['rgb']

class DeveloperContributionSerializer(S.ModelSerializer):
    project_name = S.ReadOnlyField(source='project.name')

    developer_name = S.ReadOnlyField(source='developer.name')
    developer_email = S.ReadOnlyField(source='developer.email')

    class Meta:
        model = DeveloperContribution
        fields = ['project_id', 'project_name', 'developer_name', 'developer_email', 'daily_contribution', 'commits_count']


class SimpleSerializer(S.ModelSerializer):
    status_str = S.SerializerMethodField()

    class Meta:
        model = Developer
        exclude = ['id', 'projects']

    def get_status_str(self, obj):
        return obj.get_status_display()
        
    # def __init__(self, *args, **kwargs):
    #     self.recent_weekly_activity = kwargs.pop('recent_weekly_activity', None)
    #     super().__init__(*args, **kwargs)


class DetailSerializer(SimpleSerializer):
    projects = S.SerializerMethodField()
    developer_languages = DeveloperLanguageSerializer(source='developerlanguage_set', many=True, read_only=True)
    # developer_activity = S.SerializerMethodField()
    contribution = S.SerializerMethodField()
    # recent_weekly_activity = S.SerializerMethodField()

    class Meta:
        model = Developer
        exclude = ['id', ]

    def get_projects(self, obj):
        proj = []
        for e in obj.projects.all():
            proj.append(ProjectSimpleSerializer(e).data)  # TODO: project recent activities
        return proj

    def get_contribution(self, obj):
        ret = []
        for e in DeveloperContribution.objects.filter(developer=obj).order_by('-commits_count'):
            serializer = DeveloperContributionSerializer(e)
            ret.append(serializer.data)
        return ret

    def get_developer_activity(self, obj):
        try:
            res = DeveloperActivity.objects.get(developer=obj)
            return DeveloperActivitySerializer(res).data
        except DeveloperActivity.DoesNotExist:
            # should never happen
            assert False

    def get_recent_weekly_activity(self, obj):
        return obj.recent_weekly_activity
            
