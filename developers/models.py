from django.db import models
from datetime import datetime, date
from django.utils import timezone
from rest_framework import serializers as S

from projects.models import Project
from projects.models import SimpleSerializer as ProjectSimpleSerializer

class Developer(models.Model):
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=200, unique=True)
    projects = models.ManyToManyField(Project)

    status = models.CharField(max_length=10)  # active or inactive

    first_commit_at = models.DateTimeField()
    last_commit_at = models.DateTimeField()
    contributed_days = models.IntegerField()

    def __str__(self):
        return f"{self.name} - {self.email}"

    def save(self, *args, **kwargs):
        if (timezone.now() - self.last_commit_at).days > 90:
            self.status = "inactive"
        else:
            self.status = "active"

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
        self.contributed_days = (self.last_commit_at - self.first_commit_at).days + 1

    def add_a_project(self, p):
        self.projects.add(p)


class SimpleSerializer(S.ModelSerializer):
    class Meta:
        model = Developer
        exclude = ['id', 'projects']

    recent_weekly_activity = S.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        self.recent_weekly_activity = kwargs.pop('recent_weekly_activity', None)
        super().__init__(*args, **kwargs)

    def get_recent_weekly_activity(self, obj):
        return self.recent_weekly_activity


class DetailSerializer(SimpleSerializer):
    projects = S.SerializerMethodField()

    class Meta:
        model = Developer
        exclude = ['id', ]

    def get_projects(self, obj):
        proj = []
        for e in obj.projects.all():
            proj.append(ProjectSimpleSerializer(e).data)  # TODO: project recent activities
        return proj
