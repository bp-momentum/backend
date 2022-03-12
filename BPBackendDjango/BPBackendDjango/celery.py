from __future__ import absolute_import, unicode_literals

import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj.settings')
app = Celery('celery_proj')

app.conf.update(timezone='Europe/London')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'every_15_seconds_beat': {
    'task': 'tasks.add',
    'schedule': 5,
    'args': (4, 5)
}
}


app.autodiscover_tasks()

