from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from celery.schedules import crontab

from .default import (
    CELERY_BACKEND, CELERY_BROKER, MONGODB_ALLOWED_HOSTS, MONGODB_PORT, TASK_DATABSE
)

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scrapy.settings')
'''
app = Celery('scrapy',
             broker='amqp://admin:admin@localhost',
             backend='ampq://admin:admin@localhost')
'''

app = Celery('scrapy',
             broker=CELERY_BROKER,
             backend=CELERY_BACKEND)
# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

CELERY_RESULT_BACKEND = "mongodb"
CELERY_MONGODB_BACKEND_SETTINGS = {
    "host": MONGODB_ALLOWED_HOSTS,
    "port": MONGODB_PORT,
    "database": TASK_DATABSE,
    "taskmeta_collection": "stock_taskmeta_collection",
}

# used to schedule tasks periodically and passing optional arguments
# Can be very useful. Celery does not seem to support scheduled task but only periodic
CELERYBEAT_SCHEDULE = {
    'every-minute': {
        'task': 'tasks.add',
        'schedule': crontab(minute='*/1'),
        'args': (1, 2),
    },
}


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
