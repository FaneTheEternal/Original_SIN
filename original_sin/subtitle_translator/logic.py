from typing import Tuple, Optional
from uuid import UUID

from subtitle_translator.models import SimpleUser
from subtitle_translator.translate_backend import SubtitleParser
from subtitle_translator.utility import get_parser


def prepare_env(uid: str, *, load_parser=True) -> Tuple[SimpleUser, Optional[SubtitleParser]]:
    uid = UUID(uid)
    user = SimpleUser.objects.get(uid=uid)
    if not load_parser:
        return user, None
    parser_class = get_parser(user.parser)
    assert parser_class, f'Cant find parser `{user.parser}`'
    parser: SubtitleParser = parser_class()
    if user.translators_cache:
        parser.load(cache=user.translators_cache)
    else:
        parser.load(file=user.file.path)
    return user, parser


def save_changes(user: SimpleUser, parser: SubtitleParser = None):
    if parser:
        user.parser = parser.__class__.__name__
        user.translators_cache = parser.save_cache()
    user.save()
