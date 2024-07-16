# Generated by Django 4.2 on 2024-07-10 09:04

import django.core.serializers.json
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectActiviy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('commit_sha', models.CharField(max_length=50)),
                ('author_name', models.CharField(max_length=200)),
                ('author_email', models.CharField(max_length=200)),
                ('author_datetime', models.DateTimeField()),
                ('details', models.JSONField(default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.project')),
            ],
        ),
    ]