import os
import subprocess

from django.conf import settings
from django.core.management import BaseCommand


def custom_apps_list():
    return list(
        set(app[:app.index('.')] for app in settings.INSTALLED_APPS) - {'django'}
    )


class Command(BaseCommand):
    help = 'compile flutter Web'
    ALL = '*'
    compiler_command = 'flutter'
    compiler_args = ['build', 'web']

    def print(self, some):
        self.stdout.write(str(some))

    def add_arguments(self, parser):
        parser.add_argument('apps', nargs='?', default=self.ALL, type=str)

    def handle(self, *args, **options):
        apps = options['apps']
        app_names = []
        if apps == self.ALL:
            for (dirpath, dirnames, filenames) in os.walk(settings.FLUTTER_PATH):
                app_names.extend(dirnames)
                break
        else:
            app_names.extend(apps)

        custom_apps = custom_apps_list()
        app_names = list(set(custom_apps) & set(app_names))
        self.print(f'Found {len(app_names)} apps {*app_names,}')
        for app_name in app_names:
            if app_name in custom_apps:
                self.compile(app_name)

    def compile(self, app_name):
        self.stdout.write(f'Compile {app_name}...\t', ending='')
        path = settings.FLUTTER_PATH + app_name + '\\'
        call = subprocess.Popen(
            [self.compiler_command, *self.compiler_args],
            cwd=path,
            shell=True,
            stdout=subprocess.DEVNULL,
        )
        call.wait()
        self.stdout.write(f'done({call.returncode})')
