import os

from original_sin.basic_settings import BasicSettings


class GlobalSettings(BasicSettings):
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']

    @property
    def INSTALLED_APPS(self):
        apps = super(GlobalSettings, self).INSTALLED_APPS
        apps += [
            # utility app
            'core.apps.CoreConfig',

            # chuvsu bot
            'chuvsu.apps.ChuvsuConfig',

            # old bot
            'old_bot.apps.OldBotConfig',

            # schedule service
            'schedule.apps.ScheduleConfig',

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

        db['old_bot_db'] = old_bot
        return db

    CHUVSU_VK_TOKEN = ''
    CHUVSU_VK_CONFIRMATION_TOKEN = ''
    CHUVSU_VK_SECRET_KEY = ''

    DATABASE_ROUTERS = ['original_sin.db_routs.OldBotRouter']

    @property
    def MIDDLEWARE(self):
        base = super(GlobalSettings, self).MIDDLEWARE
        white_noise = (
            # Simplified static file serving.
            # https://warehouse.python.org/project/whitenoise/
            'whitenoise.middleware.WhiteNoiseMiddleware',
        )
        return white_noise + base

    # Simplified static file serving.
    # https://warehouse.python.org/project/whitenoise/
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

