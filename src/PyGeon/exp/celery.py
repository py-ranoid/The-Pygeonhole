from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from celery.decorators import task
import django
from celery.schedules import crontab
from exp.settings import TIME_ZONE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exp.settings')
django.setup()

app = Celery('exp', include=['TDS.tasks'])

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.

app.config_from_object('django.conf:settings')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


# app.conf.beat_schedule = {
#     'scrape-every-24-hours': {
#         'task': 'nightswatch',
#         'schedule': 86400.0,
#         'args': ()
#     },
#     'checker': {
#         'task': 'noobswatch',
#         'schedule': 1800.0,
#         'args': ()
#     },
#     'scrape-CP-every-12-hours'{
#         'task': 'surdswatch',
#         'schedule': 43200.0,
#         'args': ()
#     }
# }
app.conf.beat_schedule = {
    'scrape-every-24-hours': {
        'task': 'nightswatch',
        'schedule': crontab(minute=0, hour=3),
        'args': ()
    },
    'checker': {
        'task': 'noobswatch',
        'schedule': 1800.0,
        'args': ()
    },
    'scrape-CP-every-12-hours': {
        'task': 'surdswatch',
        'schedule': crontab(minute=0, hour='*/11'),
        'args': ()
    }
}
app.conf.timezone = TIME_ZONE
