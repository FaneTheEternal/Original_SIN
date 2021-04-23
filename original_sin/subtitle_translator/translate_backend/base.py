import logging
from collections import namedtuple
from pathlib import Path
from typing import List, Tuple, Any, Dict, Union
from uuid import uuid4

from ninja import File

logger = logging.getLogger(__name__)


class BaseTranslator(object):
    name = 'base'

    def __init__(self, src: str = None, dest: str = None, force: bool = True):
        self.src = src
        self.dest = dest
        self.force = force

    def translate(self, data: str) -> str:
        result = ''
        try:
            if not self.force:
                self.check_src(data)
            result = self._translate(data)
        except AssertionError:
            logger.error('Specified src does not match detect src')
            result = data
        logger.info(f'Result `{result}`')
        return result

    def _translate(self, data):
        raise NotImplementedError

    def _detect(self, data):
        raise NotImplementedError

    def check_src(self, data: str):
        detect = self._detect(data)
        if detect:
            assert self.src == detect

    def translate_batch(self, data: List[str]) -> List[str]:
        return [self.translate(text) for text in data]

    def __str__(self):
        return str(self.__class__.__name__)


class SubToken(str):
    """Some text"""
    raw = False


class SpecialToken(SubToken):
    """Some special token"""
    raw = True


class Value:
    text_token = SubToken
    raw_token = SpecialToken

    values: List[SubToken]

    def __init__(self, s: Union[str, list, tuple]):
        if isinstance(s, (list, tuple)):
            self.values = list(s)
        else:
            self.values = []
            self._from_str(s)

    def _from_str(self, s: str):
        """Specific for each subtitle types"""
        self.values = [self.text_token(s)]

    def build(self):
        return ''.join(self.values)

    def __bool__(self):
        return bool(self.values)

    def translate(self, translator: BaseTranslator):
        values = []
        for value in self.values:
            if value.raw:
                values.append(value)
            else:
                values.append(
                    self.text_token(
                        translator.translate(str(value))
                    )
                )
        return self.__class__(values)

    def append(self, token):
        # print(token, type(token), isinstance(token, SubToken))
        if isinstance(token, SubToken):
            self.values.append(token)
        else:
            self.values.append(self.text_token(token))

    def to_obj(self):
        return [(token.raw, str(token)) for token in self.values]

    @classmethod
    def from_obj(cls, objs: List[Tuple[bool, str]]):
        return cls([SpecialToken(val) if raw else SubToken(val) for raw, val in objs])


class Row(namedtuple('RowStrict', ['pre_val', 'value', 'post_val'])):
    value: Value

    def build(self):
        return f'{self.pre_val}{self.value.build()}{self.post_val}'

    def to_obj(self) -> Tuple[str, List[Tuple[bool, str]], str]:
        return self.pre_val, self.value.to_obj(), self.post_val

    @classmethod
    def from_obj(cls, obj):
        pre, val, post = obj
        return cls(pre, Value.from_obj(val), post)


class SubtitleParser(object):
    file_ext = None

    pre_data: str
    old_data: List[Row]
    data: List[Row]
    translated: Dict[str, List[Value]]
    post_data: str

    path: Path

    loaded = False

    row_class = Row
    row_value_class = Value

    CACHE_TYPE = Tuple[
        Tuple[str, str],                                # Pre, post value
        List[Tuple[str, List[Tuple[bool, str]], str]],  # Result
        List[Tuple[str, List[Tuple[bool, str]], str]],  # Source
        Dict[str, List[List[Tuple[bool, str]]]]         # Translated
    ]

    def __init__(self):
        assert self.file_ext, 'You must be specified `file_ext`'

    def load(self, *, file: File = None, cache: CACHE_TYPE = None):
        """ May be loaded by sub file or existing translated cache """
        # logger.info('load')
        if cache:
            return self.load_cache(cache)
        try:
            file = file.read()
            self.pre_data, self.old_data, self.post_data = self._parse(file)
            self.data = self.old_data.copy()
            self.loaded = True
        except Exception as e:
            logger.error(e)
            raise

    def save_cache(self) -> CACHE_TYPE:
        pre_post = (self.pre_data, self.post_data)
        data = [row.to_obj() for row in self.data]
        old_data = [row.to_obj() for row in self.old_data]
        translated = {
            translator_name: [val.to_obj() for val in values]
            for translator_name, values in self.translated.items()
        }
        return pre_post, data, old_data, translated

    def load_cache(self, cached: CACHE_TYPE):
        try:
            pre_post, data, old_data, translated = cached
            self.pre_data, self.post_data = pre_post
            self.data = [self.row_class.from_obj(row) for row in data]
            self.old_data = [self.row_class.from_obj(row) for row in old_data]
            self.translated = {
                translator_name: [self.row_value_class.from_obj(val) for val in values]
                for translator_name, values in translated.items()
            }
            self.loaded = True
        except Exception as e:
            logger.error('Failed to load cache cause:')
            logger.error(e)

    def replace(self, index, value):
        # logger.info('replace')
        self._check_load()
        self.data[index].value = value

    def reverse(self, index):
        # logger.info('reverse')
        self._check_load()
        self.data[index] = self.old_data[index]

    def translate(self, *translators: BaseTranslator):
        # logger.info('translate')
        self._check_load()
        self.translated = dict()
        for translator in translators:
            self.translated[str(translator)] = [
                row.value.translate(translator)
                for row in self.old_data
            ]

    def fill_defaults(self):
        # logger.info('fill_defaults')
        self._check_load()
        self.data = []
        print(self.translated.keys())
        translator = list(self.translated.keys())[0]
        for value, row in zip(self.translated[translator], self.old_data):
            self.data.append(self.row_class(row.pre_val, value, row.post_val))

    def invoke(self, *translators: BaseTranslator):
        # logger.info('invoke')
        self._check_load()
        self.translate(*translators)
        self.fill_defaults()

    def build(self) -> str:
        # logger.info('build')
        self._check_load()
        data = self.pre_data + '\n'.join(row.build() for row in self.data) + self.post_data
        return data

    def _parse(self, file) -> Tuple[str, List[Any], str]:
        raise NotImplementedError

    def _check_load(self):
        assert self.loaded, 'Parser not loaded'


class DummyTranslator(BaseTranslator):
    name = 'dummy'

    def _translate(self, data):
        return f'Dummy({data})'

    def _detect(self, data):
        return None
