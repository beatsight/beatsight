from django.db import models
from rest_framework import serializers as S

from beatsight.models import TimestampedModel


class Project(TimestampedModel):
    name = models.CharField(max_length=200, unique=True)
    repo_url = models.CharField(max_length=1000)    # github/gitlab url
    repo_path = models.CharField(max_length=1000)  # repo local path
    repo_branch = models.CharField(max_length=100, default='master')      # master/dev/...

    # head_commit = models.CharField(max_length=50, default=None, null=True)
    last_stat_commit = models.CharField(max_length=50, default=None, null=True)
    last_sync_at = models.DateTimeField(default=None, null=True)

    status = models.CharField(max_length=10, default='inactive')  # active or inactive
    active_days = models.IntegerField(default=0)  # days that have code commits
    files_count = models.IntegerField(default=0)
    commits_count = models.IntegerField(default=0)
    first_commit_id = models.CharField(max_length=50, default='')
    last_commit_id = models.CharField(max_length=50, default='')
    first_commit_at = models.DateTimeField(default=None, null=True)
    last_commit_at = models.DateTimeField(default=None, null=True)
    age = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name}-{self.repo_url}"

    @property
    def head_commit(self):
        return self.last_commit_id

class SimpleSerializer(S.ModelSerializer):
    # last_commit_at = S.SerializerMethodField()
    recent_weekly_activity = S.SerializerMethodField()

    class Meta:
        model = Project
        exclude = []

    def __init__(self, *args, **kwargs):
        # self.last_commit_at = kwargs.pop('last_commit_at', None)
        self.recent_weekly_activity = kwargs.pop('recent_weekly_activity', None)
        super().__init__(*args, **kwargs)

    # def get_last_commit_at(self, obj):
    #     return self.last_commit_at

    def get_recent_weekly_activity(self, obj):
        return self.recent_weekly_activity

class DetailSerializer(SimpleSerializer):
    authors_statistics = S.SerializerMethodField()
    weekly_activity = S.SerializerMethodField()

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
    
