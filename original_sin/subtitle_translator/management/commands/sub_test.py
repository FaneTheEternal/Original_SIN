import logging
from pathlib import Path

from django.core.management import BaseCommand

from subtitle_translator.translate_backend import GoogleTranslator, AssParser, DummyTranslator

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('sub_file', nargs='+', type=str)

    def handle(self, *args, **options):
        file = Path(options['sub_file'][0])
        path = file.parent

        transaction = GoogleTranslator(src='en', dest='ru', force=False)
        logger.info(file.parent)
        parser = AssParser()
        parser.load(file=file)
        try:
            pass
            parser.invoke(transaction)
            result = parser.build()
            logger.info(result)
        except Exception as e:
            logger.error(e)
            raise
