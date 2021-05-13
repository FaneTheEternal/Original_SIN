import logging

from django.conf import settings
from django.core.management import BaseCommand

from django_flutter.utility import FlutterWrapper, get_flutter_apps


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'compile flutter Web'
    ALL = '*'

    def print(self, some, ending=None):
        self.stdout.write(str(some), ending=ending)

    def add_arguments(self, parser):
        parser.add_argument('apps', nargs='?', default=self.ALL, type=str)

    def handle(self, *args, **options):
        apps = options['apps']
        app_names = []
        if apps == self.ALL:
            app_names = get_flutter_apps()
        else:
            app_names = list(set(get_flutter_apps()) & set(app_names))

        logger.info(f'Found {len(app_names)} apps {*app_names,}')
        flutter = FlutterWrapper(
            app_list=app_names,
            release=True,
            flutter_projects_path=settings.FLUTTER_PROJECTS_PATH,
            logger=logger,
            build_params=['--web-renderer', 'html'],
        )
        flutter.invoke()
