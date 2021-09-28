import os
from pathlib import Path

import dj_database_url
from huey import RedisHuey
from redis import ConnectionPool

from original_sin.basic_settings import BasicSettings


class GlobalSettings(BasicSettings):
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']

    @property
    def INSTALLED_APPS(self):
        apps = super(GlobalSettings, self).INSTALLED_APPS
        apps += [
            # tasks app
            'huey.contrib.djhuey',

            'ordered_model',
            'bootstrap5',

            # django-storages
            # 'storages',

            # utility app
            'core.apps.CoreConfig',

            # chuvsu bot
            'chuvsu.apps.ChuvsuConfig',

            # old bot
            'old_bot.apps.OldBotConfig',

            # all bots
            'bots.apps.BotsConfig',

            # flutter
            'django_flutter.apps.DjangoFlutterConfig',

            # subtitle translator
            'subtitle_translator.apps.SubtitleTranslatorConfig',

            # atheneum
            'atheneum.apps.AtheneumConfig',

            # Информационная безопасность web-ресурсов
            'is_web.apps.IsWebConfig',

            # Аналитика сотрудников
            'hr_analytics.apps.HrAnalyticsConfig',
        ]
        return apps

    @property
    def DATABASES(self):
        db = super(GlobalSettings, self).DATABASES
        BASE_DIR = super(GlobalSettings, self).BASE_DIR

        old_bot = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'original_sin/db.sqlite3'),
        }

        # Roflan stub
        postgresql = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'original_sin/db.sqlite3'),
        }

        db['old_bot_db'] = old_bot
        db['postgresql'] = postgresql
        return db

    CHUVSU_VK_TOKEN = ''
    CHUVSU_VK_CONFIRMATION_TOKEN = ''
    CHUVSU_VK_SECRET_KEY = ''

    DATABASE_ROUTERS = ['original_sin.db_routs.OldBotRouter']

    DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

    @property
    def MIDDLEWARE(self):
        base = list(super(GlobalSettings, self).MIDDLEWARE)
        white_noise = [
            # Simplified static file serving.
            # https://warehouse.python.org/project/whitenoise/
            'whitenoise.middleware.WhiteNoiseMiddleware',
        ]
        return white_noise + base

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/1.9/howto/static-files/
    # STATIC_ROOT = os.path.join(BasicSettings.BASE_DIR, 'staticfiles')
    STATIC_URL = '/static/'
    STATICFILES_STORAGE = ''
    MEDIA_URL = '/media/'
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

    DEFAULT_ADMIN_USERNAME = 'admin'
    DEFAULT_ADMIN_PASSWORD = 'admin'

    AWS_ACCESS_KEY_ID = ''
    AWS_SECRET_ACCESS_KEY = ''
    AWS_STORAGE_BUCKET_NAME = ''
    AWS_URL = ''
    AWS_DEFAULT_ACL = None
    AWS_S3_REGION_NAME = ''
    AWS_S3_SIGNATURE_VERSION = 's3v4'

    # Development flutter path
    FLUTTER_PROJECTS_PATH = Path(BasicSettings.BASE_DIR).parent.joinpath('flutter')
    # Developer can work with partial of all flutter projects
    USE_RELEASE_FLUTTER_APPS_LIST = False
    # Release flutter apps
    FLUTTER_APPS = []

    HUEY = {
        'huey_class': 'huey.RedisHuey',  # Huey implementation to use.
        'name': 'huey_db',  # Use db name for huey.
        'results': True,  # Store return values of tasks.
        'store_none': False,  # If a task returns None, do not save to results.
        'immediate': False,  # If DEBUG=True, run synchronously.
        'utc': True,  # Use UTC for all times internally.
        'blocking': True,  # Perform blocking pop rather than poll Redis.
        'connection': {
            'host': 'localhost',
            'port': 6379,
            'db': 0,
            'connection_pool': None,  # Definitely you should use pooling!
            # ... tons of other options, see redis-py for details.

            # huey-specific connection parameters.
            'read_timeout': 1,  # If not polling (blocking pop), use timeout.
            'url': None,  # Allow Redis config via a DSN.
        },
        'consumer': {
            'workers': 1,
            'worker_type': 'thread',
            'initial_delay': 0.1,  # Smallest polling interval, same as -d.
            'backoff': 1.15,  # Exponential backoff using this rate, -b.
            'max_delay': 10.0,  # Max possible polling interval, -m.
            'scheduler_interval': 1,  # Check schedule every second, -s.
            'periodic': True,  # Enable crontab feature.
            'check_worker_health': True,  # Enable worker health checks.
            'health_check_interval': 1,  # Check worker health every second.
        },
    }

    CHUVSUGUIDE_BOT_TOKEN = ''


class EnvironmentLoadSettings(GlobalSettings):
    def get_settings(self):
        import json

        base = super(EnvironmentLoadSettings, self).get_settings()
        env = os.environ.copy()

        new_params = set(base.keys()) & set(env.keys())
        for key in new_params:
            try:
                base[key] = json.loads(env[key])
            except json.decoder.JSONDecodeError:
                base[key] = env[key]

        db_url_key = 'DATABASE_URL'
        db_list_key = 'ENV_DATABASES'
        if db_url_key in env and db_list_key in env:
            db_names = env.get(db_list_key).split(';')
            db_url = env.get(db_url_key)
            for db in db_names:
                base['DATABASES'][db] = dj_database_url.parse(
                    db_url,
                    conn_max_age=600,
                    ssl_require=True
                )

        redis_save = json.loads(env.get('REDIS_SAFE', 'false'))
        redis_url = env.get('REDIS_TLS_URL') if redis_save else env.get('REDIS_URL')
        pool = ConnectionPool.from_url(redis_url, max_connections=20)

        # Huey
        huey = RedisHuey('redis-huey', connection_pool=pool)
        base['HUEY'] = huey
        return base
