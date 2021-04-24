import logging

from googletrans import Translator

from subtitle_translator.translate_backend.base import BaseTranslator


log = logging.getLogger(__name__)


class GoogleTranslator(BaseTranslator):
    name = 'google_translate'

    url = ''

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('dest', 'en')
        kwargs.setdefault('src', 'auto')
        super(GoogleTranslator, self).__init__(*args, **kwargs)
        self.translator = Translator()

    def _detect(self, data):
        # logging.info(f'Detect `{data}`')
        result = self.translator.detect(data).lang
        return result

    def _translate(self, data):
        # logging.info(f'Translate `{data}`')
        result = self.translator.translate(data, dest=self.dest, src=self.src).text or data
        return result
