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

            # subtitle translate service
            'subtitle_translator.apps.SubtitleTranslatorConfig',
            
            # all bots
            'bots.apps.BotsConfig',
        ]
        return apps

    @property
    def DATABASES(self):
        db = super(GlobalSettings, self).DATABASES
        BASE_DIR = super(GlobalSettings, self).BASE_DIR

        old_bot = {
            'old_bot_db': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': os.path.join(BASE_DIR, 'original_sin/db.sqlite3'),
            }
        }

        db.update(old_bot)
        return db

    CHUVSU_VK_TOKEN = ''
    CHUVSU_VK_CONFIRMATION_TOKEN = ''
    CHUVSU_VK_SECRET_KEY = ''

    DATABASE_ROUTERS = ['original_sin.db_routs.OldBotRouter']

    FLUTTER_PATH = f'{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}\\..\\flutter\\'
