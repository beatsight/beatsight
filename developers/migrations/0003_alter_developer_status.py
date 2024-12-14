# Generated by Django 4.2 on 2024-12-14 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('developers', '0002_alter_developer_last_commit_at_alter_developer_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='developer',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], db_index=True, default='inactive', max_length=10),
        ),
    ]
