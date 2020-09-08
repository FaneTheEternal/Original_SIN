from original_sin.basic_settings import BasicSettings


class GlobalSettings(BasicSettings):
    ALLOWED_HOSTS = ['localhost']

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
            'schedule.apps.ScheduleConfig'
        ]
        return apps

    CHUVSU_VK_TOKEN = ''
    CHUVSU_VK_CONFIRMATION_TOKEN = ''
    CHUVSU_VK_SECRET_KEY = ''
