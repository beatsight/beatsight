import os
import shutil

from django.core.management.base import BaseCommand, CommandError
import pygit2
from pygit2 import clone_repository

from projects.models import Project
from repo_sync.models import SyncInfo

def git_pull(repo_path, branch, remote_name='origin'):
    repo = pygit2.Repository(repo_path)

    remote = repo.remotes[remote_name]
    remote.fetch()

    remote_branch = f'refs/remotes/{remote_name}/{branch}'
    merge_result, _ = repo.merge_analysis(repo.lookup_reference(remote_branch).target)
    if merge_result & pygit2.GIT_MERGE_ANALYSIS_UP_TO_DATE:
        print("Already up to date")
    elif merge_result & pygit2.GIT_MERGE_ANALYSIS_FASTFORWARD:
        remote_ref = remote.lookup_reference(remote_branch).target
        repo.checkout_tree(repo.get(remote_ref).tree)
        repo.head.set_target(remote_ref)
        print("Fast-forwarded")
    elif merge_result & pygit2.GIT_MERGE_ANALYSIS_NORMAL:
        remote_ref = remote.lookup_reference(remote_branch).target
        repo.merge(remote_ref)
        if repo.index.conflicts:
            print("Merge conflict, please resolve")
        else:
            tree_id = repo.index.write_tree()
            repo.create_commit(
                'HEAD', 
                repo.default_signature,
                repo.default_signature,
                'Merge branch',
                tree_id,
                [repo.head.target, remote_ref]
            )
            print("Merge successful")    

    return repo

REPO_PATH_PREFIX = '/tmp/beatsight'
if not os.path.exists(REPO_PATH_PREFIX):
    os.makedirs(REPO_PATH_PREFIX)

class Command(BaseCommand):
    help = "Pull repos of all projects"

    def add_arguments(self, parser):
        parser.add_argument("--project", default='', type=str)

    def handle(self, *args, **options):
        proj = options['project']

        self.stdout.write(f'start to pull repos..., project: {proj}')

        for p in Project.objects.all():
            # check whether a project has been cloned
            if proj and p.name != proj:
                continue

            clone_repo = False
            try:
                si = SyncInfo.objects.get(project=p)
            except SyncInfo.DoesNotExist:
                si = SyncInfo(project=p)
                clone_repo = True

            if clone_repo:
                repo_path = f'{REPO_PATH_PREFIX}/{p.name}'
                if os.path.exists(repo_path):
                    shutil.rmtree(repo_path)

                repo = clone_repository(p.repo_url, repo_path)
                # save repo path
                p.repo_path = repo_path
                p.save()
            else:
                assert p.repo_path
                repo = git_pull(p.repo_path, p.branch)

            head_commit = str(repo[repo.head.target].oid)
            si.head_commit = head_commit
            si.save()

            self.stdout.write(
                self.style.SUCCESS(f'Successfully pulled repo {p.name}')
            )

        self.stdout.write('Done.')
