from django.db import models

from projects.models import Project


class SyncInfo(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    head_commit = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.project.name}-{self.head_commit}"
