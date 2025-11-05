import os

from django.test import TestCase
from django import setup

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Tesla.settings")
setup()

from django_q.tasks import schedule
s = schedule('suite.task._test_task', cron="* * * * *", schedule_type="C")


