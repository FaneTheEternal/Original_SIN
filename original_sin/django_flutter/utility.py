import logging
import os
import shutil
import subprocess
import inspect
from pathlib import Path
from typing import List, Optional

from django.conf import settings

from core.utility import func_once


class FlutterWrapper(object):
    build_cmd = ['flutter', 'build', 'web']

    static_folder_name = 'flutter'

    base_url = '{{ base_path }}'

    def __init__(self,
                 *,
                 app_list: List[str] = (),
                 release: bool = False,
                 build_params: List[str] = None,
                 flutter_projects_path: Path = None,
                 logger: logging.Logger = logging.getLogger(__name__)
                 ):
        if len(app_list) < 1:
            logger.warning('Empty apps list')
        self.app_list = app_list
        self.release = release
        self.build_params = build_params
        assert isinstance(flutter_projects_path, Path)
        self.flutter_projects_path = flutter_projects_path
        self.logger = logger

    def invoke(self):
        for app in self.app_list:
            result = self.compile(app)
            if result:
                self.transfer(result, app)

    def compile(self, app_name: str) -> Optional[Path]:
        """
        Compile the flutter of a specific application
        """
        self.logger.info(f'Compile "{app_name}"...')
        path = self.flutter_projects_path.joinpath(app_name)
        cmd = self.build_cmd
        if self.release:
            cmd += ['--release']
        if self.build_params:
            cmd += self.build_params
        call = subprocess.Popen(
            cmd,
            cwd=path,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        call.wait()
        if call.returncode == 0:
            self.logger.info(f'{app_name} compiled')
            build_path = path.joinpath('build', 'web')
            self._re_build_index(build_path.joinpath('index.html'))
            return build_path
        else:
            self.logger.error(f'Some error occurred')
            text, err = call.communicate()
            self.logger.error(err)
            return None

    def transfer(self, build_path, app_name):
        """
        Copying static files and template
        """
        static_path = Path(settings.BASE_DIR).joinpath(app_name, self.static_folder_name)
        static_path.mkdir(parents=True, exist_ok=True)
        build_path = Path(build_path)
        self.logger.info('Removing old flutter static files...')
        shutil.rmtree(static_path)
        self.logger.info('Copy new files...')
        shutil.copytree(build_path, static_path)

        self.logger.info('Copy base template...')
        template_path = static_path.parent.joinpath('templates', app_name)
        template_path.mkdir(parents=True, exist_ok=True)
        shutil.copy2(build_path.joinpath('index.html'), template_path.joinpath('index.html'))

        self.logger.info(f'"{app_name}" files transferred')

    def _re_build_index(self, path: Path):
        file = open(path, 'r').read()
        find = '<base href="/">'
        try:
            pos = file.index(find)
            file = file[:pos] + f'<base href="{self.base_url}">' + file[pos + len(find):]
            open(path, 'w').write(file)
        except:
            pass


@func_once
def get_flutter_apps():
    if not settings.DEBUG or settings.USE_RELEASE_FLUTTER_APPS_LIST:
        return settings.FLUTTER_APPS
    settings_apps = set(
        app[:app.index('.')] if '.' in app else app
        for app in settings.INSTALLED_APPS
    ) - {'django'}
    flutter_apps = set()
    for (dirpath, dirnames, filenames) in os.walk(settings.FLUTTER_PROJECTS_PATH):
        flutter_apps.update(dirnames)
    return list(flutter_apps & settings_apps)
