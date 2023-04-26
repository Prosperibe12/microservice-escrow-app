from __future__ import absolute_import, unicode_literals

import os
from celery import Celery
from decouple import config

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_core.settings')

app = Celery('project_core', broker=config('AMPQ_URL'))
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
