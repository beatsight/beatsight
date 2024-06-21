from django.db import models
from django.utils import timezone
from rest_framework import serializers as S

from beatsight.models import TimestampedModel
from beatsight.consts import ACTIVE, INACTIVE

class Language(TimestampedModel):
    name = models.CharField(max_length=255, primary_key=True)

    def __str__(self):
        return self.name

class LanguageSerializer(S.ModelSerializer):
    class Meta:
        model = Language
        fields = ['name']


class Project(TimestampedModel):
    PROJ_STATUS = (
        (ACTIVE, '活跃'),
        (INACTIVE, '不活跃')
    )

    name = models.CharField(max_length=200, unique=True)
    repo_url = models.CharField(max_length=1000)    # github/gitlab url
    repo_path = models.CharField(max_length=1000)  # repo local path
    repo_branch = models.CharField(max_length=100, default='master')      # master/dev/...

    # head_commit = models.CharField(max_length=50, default=None, null=True)
    last_stat_commit = models.CharField(max_length=50, default=None, null=True)
    last_sync_at = models.DateTimeField(default=None, null=True)

    status = models.CharField(max_length=10, choices=PROJ_STATUS, default=INACTIVE)
    active_days = models.IntegerField(default=0)  # days that have code commits
    age = models.IntegerField(default=0)
    active_days_ratio = models.FloatField(default=0)
    files_count = models.IntegerField(default=0)
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

    def save(self, *args, **kwargs):
        if self.last_commit_at and (timezone.now() - self.last_commit_at).days > 90:
            self.status = INACTIVE
        else:
            self.status = ACTIVE

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

class ProjectLanguageSerializer(S.ModelSerializer):
    language_name = S.ReadOnlyField(source='language.name')

    class Meta:
        model = ProjectLanguage
        fields = ['language_name', 'lines_count']
    
class SimpleSerializer(S.ModelSerializer):
    recent_weekly_activity = S.SerializerMethodField()
    status_str = S.SerializerMethodField()

    class Meta:
        model = Project
        exclude = []

    def __init__(self, *args, **kwargs):
        self.recent_weekly_activity = kwargs.pop('recent_weekly_activity', None)
        super().__init__(*args, **kwargs)

    def get_status_str(self, obj):
        return obj.get_status_display()

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
        for e in ProjectLanguage.objects.filter(project=obj)[:5]:
            ret.append(ProjectLanguageSerializer(e).data)
        return ret
