# poc_server/celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'poc_server.settings')

app = Celery('poc_server')
# broker URL — use env var or default to redis for dev
app.conf.broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')

# you can use JSON to keep things simple
app.conf.accept_content = ['json']
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'

app.autodiscover_tasks()
