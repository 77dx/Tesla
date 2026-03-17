import os

from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Tesla.settings")

app = Celery("Tesla")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

