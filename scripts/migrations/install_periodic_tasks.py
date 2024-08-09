from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', 'create_superuser'),
    ]

    def install(apps, schema_editor):
        import zoneinfo
        from django_celery_beat.models import CrontabSchedule, PeriodicTask

        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute='10',
            hour='*',
            day_of_week='*',
            day_of_month='*',
            month_of_year='*',
            timezone=zoneinfo.ZoneInfo('Asia/Shanghai')
        )

        task = 'projects.tasks.update_repo_task'
        if PeriodicTask.objects.get(task=task):
            print(f'task {task} already installed')
        else:
            PeriodicTask.objects.create(
                crontab=schedule,
                name='Update Repos',
                task=task,
            )
            print(f'successfully installed task {task}')

        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute='60',
            hour='*',
            day_of_week='*',
            day_of_month='*',
            month_of_year='*',
            timezone=zoneinfo.ZoneInfo('Asia/Shanghai')
        )

        task = 'projects.tasks.clean_orphan_developers'
        if PeriodicTask.objects.get(task=task):
            print(f'task {task} already installed')
        else:
            PeriodicTask.objects.create(
                crontab=schedule,
                name='Clean Orphan Devs',
                task=task,
            )
            print(f'successfully installed task {task}')


    operations = [
        migrations.RunPython(install),
    ]
            
