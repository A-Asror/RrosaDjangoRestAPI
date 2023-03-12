#!/bin/sh


# Install package
pip install -r requirements/dev.txt

# run a worker :) --concurrency 1 -E
#celery -A core worker -l info --detach
celery -A core worker -l warning
# celery -A core beat -l info --detach --scheduler django_celery_beat.schedulers:DatabaseScheduler

exec "$@"
