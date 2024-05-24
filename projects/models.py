from django.db import models
from rest_framework import serializers as S

class Project(models.Model):
    name = models.CharField(max_length=200)
    repo_url = models.CharField(max_length=1000)    # github/gitlab url
    repo_path = models.CharField(max_length=1000)  # repo local path
    branch = models.CharField(max_length=100)      # master/dev/...

    def __str__(self):
        return f"{self.name}-{self.repo_url}"

class SimpleSerializer(S.ModelSerializer):
    last_commit_date = S.SerializerMethodField()
    recent_weekly_activity = S.SerializerMethodField()

    class Meta:
        model = Project
        exclude = ['id', ]

    def __init__(self, *args, **kwargs):
        self.last_commit_date = kwargs.pop('last_commit_date', None)
        self.recent_weekly_activity = kwargs.pop('recent_weekly_activity', None)
        super().__init__(*args, **kwargs)

    def get_last_commit_date(self, obj):
        return self.last_commit_date

    def get_recent_weekly_activity(self, obj):
        return self.recent_weekly_activity

class DetailSerializer(SimpleSerializer):
    top_authors_statistics = S.SerializerMethodField()

    class Meta:
        model = Project
        exclude = ['id', ]

    def __init__(self, *args, **kwargs):
        self.top_authors_statistics = kwargs.pop('top_authors_statistics', None)
        super().__init__(*args, **kwargs)

    def get_top_authors_statistics(self, obj):
        return self.top_authors_statistics
