import time
from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django Command to handle the commands of db connection wait"""

    def handle(self, *args, **options):
        self.stdout.write('Checking the connection availability')
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']
            except OperationalError:
                self.stdout.write('Waiting for db to get up')
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('DB is available'))
