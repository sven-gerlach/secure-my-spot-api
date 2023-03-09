"""
Django command to wait for the db initialisation
Source: https://youtu.be/mScd-Pc_pX0?t=2917
"""

import time
from psycopg2 import OperationalError as Psycop2OpError
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Django command to wait for db loading completed
    """
    help = "Django command to wait for db loading completed"

    def handle(self, *args, **options):
        """

        """
        self.stdout.write("Waiting for database...")
        db_is_loaded = False
        while db_is_loaded is False:
            try:
                self.check(databases=["default"])
                db_is_loaded = True
            except (Psycop2OpError, OperationalError):
                self.stdout.write("Database not loaded yet, waiting 1 second...")
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS("Database ready!"))