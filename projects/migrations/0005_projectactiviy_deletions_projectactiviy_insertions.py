# Generated by Django 4.2 on 2024-07-19 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_projectactiviy_commit_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectactiviy',
            name='deletions',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='projectactiviy',
            name='insertions',
            field=models.IntegerField(default=0),
        ),
    ]
