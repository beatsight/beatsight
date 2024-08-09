from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    def generate_superuser(apps, schema_editor):
        import os
        from django.contrib.auth.models import User

        DJANGO_SU_NAME = os.environ.get('DJANGO_SU_NAME', 'foo')
        DJANGO_SU_EMAIL = os.environ.get('DJANGO_SU_EMAIL', 'foo@foo.com')
        DJANGO_SU_PASSWORD = os.environ.get('DJANGO_SU_PASSWORD', 'foo')

        user = User.objects.get(username=DJANGO_SU_NAME)
        if user:
            print(f'user {DJANGO_SU_NAME} already created')
            return

        superuser = User.objects.create_superuser(
            username=DJANGO_SU_NAME,
            email=DJANGO_SU_EMAIL,
            password=DJANGO_SU_PASSWORD)

        superuser.save()

    operations = [
        migrations.RunPython(generate_superuser),
    ]
