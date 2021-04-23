import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.UserModel = get_user_model()
        self.username_field = self.UserModel._meta.get_field(self.UserModel.USERNAME_FIELD)

    def handle(self, *args, **options):
        logger.info('FIX ADMIN USER')
        username = getattr(settings, 'DEFAULT_ADMIN_USERNAME', 'admin')
        password = getattr(settings, 'DEFAULT_ADMIN_PASSWORD', 'admin')
        deleted = self.UserModel.objects.filter(username=username).delete()
        logger.info(f'Deleted {deleted} users')
        self.UserModel.objects.create_user(username=username, password=password, is_staff=True, is_superuser=True)
        logger.info(f'ADMIN {username}:{password[0]}{"*" * (len(password) - 2)}{password[-1]}')

