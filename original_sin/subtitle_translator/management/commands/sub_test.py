import logging
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management import BaseCommand

from subtitle_translator.translate_backend import GoogleTranslator, AssParser, DummyTranslator

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('sub_file', nargs='+', type=str)

    def handle(self, *args, **options):
        file = Path(options['sub_file'][0])
        path = file.parent
        result_path = path.joinpath('qq.ass')
        file = ContentFile(open(file, mode='rb').read())

        transaction = DummyTranslator(src='en', dest='ru', force=True)
        parser = AssParser()
        parser.load(file=file)
        try:
            # raise RuntimeError('INTERRUPTION')
            parser.invoke(transaction)
            result = parser.build()
            open(result_path, mode='w').write(result.replace('\r', ''))
        except Exception as e:
            logger.error(e)
            # raise
