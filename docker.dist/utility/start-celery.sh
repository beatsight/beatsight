#!/usr/bin/env bash

cd /home/ubuntu/beatsight && python3 -m celery -A beatsight worker --loglevel=info
