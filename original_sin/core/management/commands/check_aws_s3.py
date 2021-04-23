import logging
from pathlib import Path

import boto3
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.info('CHECK AWS S3 STORAGE')
        AWS_STORAGE_BUCKET_NAME = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None)
        local_file_name = 'ini.txt'
        local_file = Path(getattr(settings, 'STATIC_ROOT')).joinpath(local_file_name)
        try:
            assert AWS_STORAGE_BUCKET_NAME, 'You must set AWS_STORAGE_BUCKET_NAME in django settings'
            s3 = boto3.resource('s3')

            logger.info('test listing')
            bucket = s3.Bucket(AWS_STORAGE_BUCKET_NAME)
            print([f.key for f in bucket.objects.all()][:10])

            logger.info('test uploading')
            data = open(local_file, 'rb')
            bucket.put_object(Key=local_file_name, Body=data)

            logger.info('test downloading')
            bucket.download_file(local_file_name, local_file.name)

        except Exception as e:
            logger.error(f'ERROR CAUSE: {e}')
        username = getattr(settings, 'DEFAULT_ADMIN_USERNAME', 'admin')
        password = getattr(settings, 'DEFAULT_ADMIN_PASSWORD', 'admin')

