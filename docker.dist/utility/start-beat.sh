#!/bin/bash

set -o nounset
set -o errexit

PIDFILE='/tmp/celerybeat.pid'

trap "rm ${PIDFILE} ; exit 130" SIGINT
trap "rm ${PIDFILE} ; exit 137" SIGKILL
trap "rm ${PIDFILE} ; exit 143" SIGTERM

if [[ -f $PIDFILE ]]
then
  rm $PIDFILE
fi

# exec python3 manage.py watch_celery_beat

cd /home/ubuntu/beatsight && python -m celery -A beatsight beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
