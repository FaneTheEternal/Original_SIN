import inspect
from typing import Optional, Type

from core.utility import func_once, my_import
from subtitle_translator.translate_backend import SubtitleParser, BaseTranslator


@func_once
def allowed_subtitles():
    from . import translate_backend
    extensions = []
    for clazz in translate_backend.__all__:
        clazz = my_import(f'subtitle_translator.translate_backend.{clazz}')
        if issubclass(clazz, translate_backend.SubtitleParser) and clazz.file_ext:
            extensions.append(clazz.file_ext)
    return extensions


@func_once
def allowed_subtitles_dict():
    from . import translate_backend
    extensions = {}
    for clazz in translate_backend.__all__:
        clazz = my_import(f'subtitle_translator.translate_backend.{clazz}')
        if issubclass(clazz, translate_backend.SubtitleParser) and clazz.file_ext:
            extensions[clazz.file_ext] = clazz
    return extensions


@func_once
def allowed_translations():
    from . import translate_backend
    translations = []
    excluded = ['base']
    for clazz in translate_backend.__all__:
        clazz = my_import(f'subtitle_translator.translate_backend.{clazz}')
        if issubclass(clazz, translate_backend.BaseTranslator) and clazz.name not in excluded:
            translations.append(clazz.__name__)
    return translations


def get_parser(parser_ext: str) -> Optional[Type[SubtitleParser]]:
    try:
        return allowed_subtitles_dict()[parser_ext]
    except ImportError:
        return None


def get_translator(translator_name: str) -> Optional[BaseTranslator]:
    try:
        return my_import(f'subtitle_translator.translate_backend.{translator_name}')
    except ImportError:
        return None
