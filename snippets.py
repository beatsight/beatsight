"""sqlite select result with collumn names
.headers ON
"""

from projects.models import Project

Project.objects.all()

p = Project(name='sicp', repo_url='https://github.com/xiez/SICP-exercises.git', repo_path='', branch='master')
p.save()

from repo_sync.models import SyncInfo

SyncInfo.objects.all()

si = SyncInfo(project=p, last_commit='')
si.save()

SyncInfo.objects.all()


find . - path "*/migrations/*.py" -not -name "__init__.py" -delete
find . - path "*/migrations/*.pyc" -delete  # Also deletes compiled Python files (.pyc)
