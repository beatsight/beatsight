import os
import shutil

from django.core.management.base import BaseCommand, CommandError
import pygit2
from pygit2 import clone_repository

from projects.models import Project
from stats.views import get_a_project_stat

class Command(BaseCommand):
    help = "Make state of a project"

    def add_arguments(self, parser):
        parser.add_argument("--project", default='', type=str)
        parser.add_argument("--force", default=False, type=bool)

    def handle(self, *args, **options):
        proj = options['project']
        if not proj:
            self.style.WARNING('project name is required')
            return

        force = options['force']
        self.stdout.write(f'start to stat project: {proj}, force: {force}')

        proj = Project.objects.get(name=proj)
        get_a_project_stat(proj, force=force)

        self.stdout.write(
            self.style.SUCCESS(f'Successfully stat project: {proj.name}')
        )
