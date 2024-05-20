from django.db import models

class Project(models.Model):
    name = models.CharField(max_length=200)
    repo_url = models.CharField(max_length=1000)    # github/gitlab url
    repo_path = models.CharField(max_length=1000)  # repo local path
    branch = models.CharField(max_length=100)      # master/dev/...

    def __str__(self):
        return f"{self.name}-{self.repo_url}"
