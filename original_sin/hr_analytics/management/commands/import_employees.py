import logging

from django.core.management import BaseCommand

from hr_analytics.logic import import_employees

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        import_employees()
