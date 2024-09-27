#!/bin/bash

cd /home/ubuntu/beatsight && python -m celery -A beatsight worker --loglevel=info
