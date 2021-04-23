import logging
from pathlib import Path

from huey.contrib.djhuey import task

from core.utility import construct
from subtitle_translator.models import SimpleUser
from subtitle_translator.translate_backend import SubtitleParser
from subtitle_translator.utility import get_translator

logger = logging.getLogger(__name__)


@task()
def translate_invoke(user: SimpleUser, parser: SubtitleParser):
    print('translate_invoke')
    user.translators_cache = None
    user.save()
    parser.load(file=user.file)
    translators = []
    for name in user.translators:
        translator = get_translator(name)
        if translators is not None:
            translators.append(translator)
    translators = construct(*translators, **user.translators_params)
    print(translators)
    parser.translate(*translators)
    parser.fill_defaults()
    user.translators_cache = parser.save_cache()
    user.save()
