# Generated by Django 4.2 on 2024-12-20 07:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0014_alter_project_status_alter_project_sync_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='lines_code',
            field=models.BigIntegerField(db_index=True, default=0),
        ),
    ]
