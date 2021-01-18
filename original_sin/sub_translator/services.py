import re

from googletrans import Translator


class TranslateBackend:
    src = 'en'
    dest = 'ru'

    def __init__(self):
        pass

    def translate(self, txt):
        raise NotImplementedError

    @property
    def verbose_name(self):
        raise NotImplementedError


class GoogleTranslateBackend(TranslateBackend):
    def __init__(self):
        super(GoogleTranslateBackend, self).__init__()
        self.translator = Translator()

    @property
    def verbose_name(self):
        return 'Google Translate'

    def translate(self, txt):
        result = self.translator.translate(text=txt, dest=self.dest, src=self.src)
        return result.text


class SubBackend:
    file_types: list
    file = None

    reg = re.compile(r'\[([a-zA-Z]+)\](.*)')

    def __init__(self, file_name, translator: TranslateBackend):
        self.translator = translator
        self.file_name = file_name

        self.file = open(f'./{self.file_name}.{self.file_type}')

    def execute(self):
        raise NotImplementedError


class SoftSubBackend(SubBackend):
    file_types = ('srt', 'sub', 'txt')
    result = []

    class STR:
        def __init__(self, pos, timeline, text):
            self.pos = pos
            self.timeline = timeline
            self.text = text

    def execute(self):
        text = self.file.read()
        self.file.close()
        blocks = text.split('\n\n')
        sources = []
        for block in blocks:
            pos, timeline, texts = block.split('\n')
            sources.append(self.STR(
                pos=int(pos),
                timeline=timeline,
                text=''.join(texts)
            ))

        for source in sources:
            self.result.append(self.STR(
                pos=source.pos,
                timeline=source.timeline,
                text=self.translator.translate(source.text)
            ))

    def save(self):
        text = '\n\n'.join(f'{block.pos}\n{block.timeline}\n{block.text}' for block in self.result)
        new_file_name = f'[{self.translator.dest}]{self.file_name}'
        new_file = open(new_file_name, 'w+')
        new_file.write(text)
        new_file.close()
        return new_file_name
