import os
import shutil

from django.core.management.base import BaseCommand, CommandError
import pygit2
from pygit2 import clone_repository

from projects.models import Project
from stats.views import get_a_project_stat
from beatsight.utils.git import test_repo_and_branch, full_clone_repo_with_branch


class Command(BaseCommand):
    help = "Make state of a project"

    def add_arguments(self, parser):
        parser.add_argument("--url", default='', type=str)
        parser.add_argument("--branch", default='', type=str)

    def handle(self, *args, **options):
        repo_url = options['url']
        if not repo_url:
            self.style.WARNING('project url is required')
            return

        repo_branch = options['branch']
        if not repo_branch:
            self.style.WARNING('project url is required')
            return

        name = repo_url.split('/')[-1].split('.')[0]
        test_repo_and_branch(repo_url, name, repo_branch)
        local_path = full_clone_repo_with_branch(repo_url, name, repo_branch)

        self.stdout.write(
            self.style.SUCCESS(f'Successfully cloned project: {repo_url} to {local_path}')
        )
