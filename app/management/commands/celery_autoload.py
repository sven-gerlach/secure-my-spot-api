"""
Script to utilise django's auto-load feature for restarting celery on any file change
Source: https://stackoverflow.com/questions/43919166/django-and-celery-re-loading-code-into-celery
-after-a-change
"""

import shlex
import subprocess
import sys

from django.core.management.base import BaseCommand
from django.utils import autoreload


class Command(BaseCommand):
    def handle(self, *args, **options):
        autoreload.run_with_reloader(self._restart_celery)

    @classmethod
    def _restart_celery(cls):
        if sys.platform == "win32":
            cls.run("taskkill /f /t /im celery.exe")
            cls.run("celery -A phoenix worker --loglevel=info --pool=solo")
        else:
            cls.run("pkill celery")
            cls.run("celery -A secure_my_spot.celeryconf worker --loglevel=INFO")

    @staticmethod
    def run(cmd):
        subprocess.call(shlex.split(cmd))
