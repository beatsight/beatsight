"""
This file is part of Beatsight.

Copyright (C) 2024-2025 Beatsight Ltd.
Licensed under the GNU General Public License v3.0.
"""

import random

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers as S

from beatsight.models import TimestampedModel
from beatsight.consts import (
    INIT, CONN_SUCCESS, CONN_ERROR,
    STATING, STAT_SUCCESS, STAT_ERROR,
)
from beatsight.utils.pl_color import PL_COLOR

class Language(TimestampedModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class LanguageSerializer(S.ModelSerializer):
    class Meta:
        model = Language
        fields = ['name']


class Project(TimestampedModel):
    SYNC_STATUS = (
        (INIT, _('Init')),
        (CONN_SUCCESS, _('Conn. OK')),
        (CONN_ERROR, _('Conn. Error')),
    )

    STATUS = (
        (STATING, _('Processing')),
        (STAT_SUCCESS, _('Stat Success')),
        (STAT_ERROR, _('Stat Failed')),
    )

    name = models.CharField(max_length=200, unique=True)
    desc = models.CharField(max_length=2048, default='')
    repo_url = models.CharField(max_length=1000, db_index=True)    # github/gitlab url
    repo_branch = models.CharField(max_length=100, default='master')      # master/dev/...
    repo_path = models.CharField(max_length=1000, default='')  # repo local path
    ignore_list = models.TextField(default='')

    last_stat_commit = models.CharField(max_length=50, default=None, null=True)
    last_sync_at = models.DateTimeField(default=None, null=True)
    sync_status = models.CharField(max_length=20, choices=SYNC_STATUS, default=INIT, db_index=True)
    error_log = models.CharField(max_length=2048, default='')

    status = models.CharField(max_length=20, choices=STATUS, default=STATING, db_index=True)

    is_active = models.BooleanField(default=False)
    active_days = models.IntegerField(default=0)  # days that have code commits
    age = models.IntegerField(default=0)
    active_days_ratio = models.FloatField(default=0, db_index=True)
    files_count = models.IntegerField(default=0, db_index=True)
    lines_code = models.BigIntegerField(default=0, db_index=True)
    commits_count = models.IntegerField(default=0)
    first_commit_id = models.CharField(max_length=50, default='')
    last_commit_id = models.CharField(max_length=50, default='')
    first_commit_at = models.DateTimeField(default=None, null=True)
    last_commit_at = models.DateTimeField(default=None, null=True)

    def __str__(self):
        return f"{self.name}-{self.repo_url}"

    @property
    def head_commit(self):
        return self.last_commit_id

    def get_ignore_list(self):
        return [e.strip() for e in self.ignore_list.split('\n')]

    def sync_success(self):
        self.sync_status = CONN_SUCCESS
        self.error_log = ''
        self.last_sync_at = timezone.now()

    def sync_error(self, err_msg):
        self.sync_status = CONN_ERROR
        self.error_log = err_msg

    def is_stating(self):
        return self.status == STATING

    def start_stat(self):
        self.status = STATING

    def stat_success(self):
        self.status = STAT_SUCCESS
        self.error_log = ''

    def stat_error(self, err_msg):
        self.status = STAT_ERROR
        self.error_log = err_msg

    def save(self, *args, **kwargs):
        if self.last_commit_at and (timezone.now() - self.last_commit_at).days > 90:
            self.is_active = False
        else:
            self.is_active = True

        if self.age == 0:
            self.active_days_ratio = 0
        else:
            self.active_days_ratio = round(self.active_days / self.age, 2)
        return super().save(*args, **kwargs)

class ProjectLanguage(TimestampedModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    lines_count = models.IntegerField()

    def __str__(self):
        return f"{self.project.name} - {self.language.name}"


class ProjectActivity(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    commit_sha = models.CharField(max_length=50)
    commit_message = models.TextField(default='')
    author_name = models.CharField(max_length=200)
    author_email = models.CharField(max_length=200, db_index=True)
    author_datetime = models.DateTimeField(db_index=True)
    details = models.JSONField(default=dict, encoder=DjangoJSONEncoder)
    insertions = models.IntegerField(default=0)
    deletions = models.IntegerField(default=0)
    # 剔除异常改动，修正后的数据
    corrected_insertions = models.IntegerField(default=0)
    corrected_deletions = models.IntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['project', 'commit_sha'], name='unique_proj_commit')
        ]


class ProjectIgnoreList(models.Model):
    ...

#################### serializers
class ProjectLanguageSerializer(S.ModelSerializer):
    language_name = S.ReadOnlyField(source='language.name')
    language_color = S.SerializerMethodField()

    class Meta:
        model = ProjectLanguage
        fields = ['language_name', 'language_color', 'lines_count']

    def get_language_color(self, obj):
        d = PL_COLOR.get(obj.language.name)
        if not d:
            red = random.randint(0, 255)
            green = random.randint(0, 255)
            blue = random.randint(0, 255)
            return red, green, blue
        return d['rgb']

class ProjectActivitySerializer(S.ModelSerializer):
    project_id = S.ReadOnlyField(source='project.id')
    project_name = S.ReadOnlyField(source='project.name')
    details_str = S.SerializerMethodField()
    commit_link = S.SerializerMethodField()

    class Meta:
        model = ProjectActivity
        exclude = []

    def get_details_str(self, obj):
        ret = []
        for k, v in obj.details.items():
            if not v:
                continue

            if k == 'A':
                action = _('Added')
            elif k == 'M':
                action = _('Modified')
            elif k == 'D':
                action = ('Deleted')
            elif k == 'R':
                action = _('Renamed')
            else:
                assert False, 'invalid key'

            if isinstance(v[0], str):
                if len(v) == 1:
                    ret.append(f'{action} {v[0]}')
                else:
                    ret.append(_('{} {} and {} other files').format(action, v[0], len(v) - 1))
            elif isinstance(v[0], dict):
                val = v[0]['file_path']

                if len(v) == 1:
                    ret.append(f"{action} {val}")
                else:
                    ret.append(_('{} {} and {} other files').format(action, val, len(v) - 1))
            else:
                assert False, 'invalid value type'

        return '; '.join(ret)

    def get_commit_link(self, obj):
        for url_patt, host in settings.PROJECT_REPO_URL_MAP.items():
            if url_patt in obj.project.repo_url:
                uri = obj.project.repo_url.split(':')[1].replace('.git', '')
                return f'{host}/{uri}/commit/{obj.commit_sha}'
        return '#'

class SimpleSerializer(S.ModelSerializer):
    recent_weekly_activity = S.SerializerMethodField()
    status_str = S.SerializerMethodField()
    sync_status_str = S.SerializerMethodField()

    class Meta:
        model = Project
        exclude = []

    def __init__(self, *args, **kwargs):
        self.recent_weekly_activity = kwargs.pop('recent_weekly_activity', None)
        super().__init__(*args, **kwargs)

    def get_status_str(self, obj):
        return obj.get_status_display()

    def get_sync_status_str(self, obj):
        return obj.get_sync_status_display()

    def get_recent_weekly_activity(self, obj):
        return self.recent_weekly_activity

class DetailSerializer(SimpleSerializer):
    authors_statistics = S.SerializerMethodField()
    weekly_activity = S.SerializerMethodField()
    languages = S.SerializerMethodField()

    class Meta:
        model = Project
        exclude = []

    def __init__(self, *args, **kwargs):
        self.authors_statistics = kwargs.pop('authors_statistics', None)
        self.weekly_activity = kwargs.pop('weekly_activity', None)
        super().__init__(*args, **kwargs)

    def get_authors_statistics(self, obj):
        return self.authors_statistics

    def get_weekly_activity(self, obj):
        return self.weekly_activity

    def get_languages(self, obj):
        ret = []
        for e in ProjectLanguage.objects.filter(project=obj):
            ret.append(ProjectLanguageSerializer(e).data)
        return ret
