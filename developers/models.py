from django.db import models

# Create your models here.
class Developer(models.Model):
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    status = models.CharField(max_length=10)  # active or inactive

    first_commit_date = models.DateTimeField()
    last_commit_date = models.DateTimeField()
