#!/usr/bin/env bash

cd /home/ubuntu/beatsight && python3 -m celery -A beatsight beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
