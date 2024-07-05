# Generated by Django 4.2 on 2024-07-05 10:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
                ('name', models.CharField(max_length=200, unique=True)),
                ('repo_url', models.CharField(max_length=1000)),
                ('repo_branch', models.CharField(default='master', max_length=100)),
                ('repo_path', models.CharField(default='', max_length=1000)),
                ('last_stat_commit', models.CharField(default=None, max_length=50, null=True)),
                ('last_sync_at', models.DateTimeField(default=None, null=True)),
                ('sync_status', models.CharField(choices=[('init', '初始化'), ('conn_success', '连接成功'), ('conn_error', '连接失败'), ('stating', '统计中'), ('stat_success', '统计完成'), ('stat_error', '统计失败')], default='init', max_length=20)),
                ('status', models.CharField(choices=[('active', '活跃'), ('inactive', '不活跃')], default='inactive', max_length=20)),
                ('active_days', models.IntegerField(default=0)),
                ('age', models.IntegerField(default=0)),
                ('active_days_ratio', models.FloatField(default=0)),
                ('files_count', models.IntegerField(default=0)),
                ('commits_count', models.IntegerField(default=0)),
                ('first_commit_id', models.CharField(default='', max_length=50)),
                ('last_commit_id', models.CharField(default='', max_length=50)),
                ('first_commit_at', models.DateTimeField(default=None, null=True)),
                ('last_commit_at', models.DateTimeField(default=None, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProjectLanguage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
                ('lines_count', models.IntegerField()),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.language')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.project')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
