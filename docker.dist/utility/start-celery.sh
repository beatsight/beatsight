#!/usr/bin/env bash

cd /home/beatsight/app && gosu beatsight bash -c 'python3 -m celery -A beatsight worker --loglevel=info'
