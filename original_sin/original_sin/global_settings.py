import os

import dj_database_url

from original_sin.basic_settings import BasicSettings


class GlobalSettings(BasicSettings):
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']

    @property
    def INSTALLED_APPS(self):
        apps = super(GlobalSettings, self).INSTALLED_APPS
        apps += [
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
    MEDIA_URL = '/static/'
    DEFAULT_FILE_STORAGE = ''

    # Extra places for collectstatic to find static files.
    # STATICFILES_DIRS = (
    #     os.path.join(BasicSettings.BASE_DIR, 'static'),
    # )

    # Simplified static file serving.
    # https://warehouse.python.org/project/whitenoise/
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

    DEFAULT_ADMIN_USERNAME = 'admin'
    DEFAULT_ADMIN_PASSWORD = 'admin'

    AWS_ACCESS_KEY_ID = ''
    AWS_SECRET_ACCESS_KEY = ''
    AWS_STORAGE_BUCKET_NAME = ''
    AWS_URL = ''
    AWS_DEFAULT_ACL = None
    AWS_S3_REGION_NAME = ''
    AWS_S3_SIGNATURE_VERSION = 's3v4'


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
        return base
