class BasicRouter(object):
    route_app_labels = set()

    def __not_implement(self, f_name):
        raise NotImplementedError(f'Should be implement {f_name}')

    def db_for_read(self, model, **hints):
        self.__not_implement(__name__)

    def db_for_write(self, model, **hints):
        self.__not_implement(__name__)

    def allow_relation(self, obj1, obj2, **hints):
        self.__not_implement(__name__)

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        self.__not_implement(__name__)


class OldBotRouter(BasicRouter):
    """
    A router to control all database operations on models in the
    old_bot and contenttypes applications.
    """
    route_app_labels = {'old_bot'}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return 'old_bot_db'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return 'old_bot_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if (
            obj1._meta.app_label in self.route_app_labels and
            obj2._meta.app_label in self.route_app_labels
        ):
            return True

        if (
            obj1._meta.app_label in self.route_app_labels or
            obj2._meta.app_label in self.route_app_labels
        ):
            return False
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == 'old_bot_db'
        return None
