#!/usr/bin/env bash

cd /home/beatsight/app && gosu beatsight bash -c 'python3 -m celery -A beatsight beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler'
