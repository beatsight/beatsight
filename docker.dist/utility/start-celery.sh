#!/usr/bin/env bash

cd /home/ubuntu/beatsight && gosu ubuntu bash -c 'python3 -m celery -A beatsight worker --loglevel=info'
