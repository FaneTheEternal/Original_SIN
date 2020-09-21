import json
import os
from datetime import timedelta, datetime
from string import ascii_uppercase

from django.utils.timezone import now

from ..models import GameProfile, VkUser

GAME_MAP = [
    '##########',
    '##########',
    '###@######',
    '##########',
    '#####@####',
    '##@#######',
    '##########',
    '####@#####',
    '##########',
    '##########',
]

CLOSE = '#'
EMPTY = '_'
TREASURES = {
    '@': (10, '%'),
}

TREASURE_AWARD = 10


class Game(object):
    X = 9  # 10
    Y = 9  # 10

    game_title = 'warships'
    default_data_set = {
        'score': 0,
        'last_call': None,  # datetime
        'extension': ''
    }

    recovery = 10
    date_format = '%Y-%m-%d %H:%M:%S.%f %Z'

    vk = None
    GAME_MAP = None

    def __init__(self, **kwargs):
        self.user = kwargs.pop('user')
        self.vk = kwargs.pop('vk', None)
        self.profile, created = GameProfile.objects.using('old_bot').get_or_create(
            user=self.user
        )
        self.big_data = json.loads(self.profile.some_data)
        self.data = self.big_data.get(self.game_title, self.default_data_set)

        # load data
        last_call = self.data['last_call']
        if last_call:
            self.data['last_call'] = datetime.strptime(last_call, self.date_format)

        self._load_map()

    def save(self):
        def _dumps(o):
            if isinstance(o, datetime):
                return o.strftime(self.date_format)
            return o
        self.big_data[self.game_title] = self.data
        self.profile.some_data = json.dumps(self.big_data, default=_dumps)
        self.profile.save()

    def _load_map(self):
        if self.vk is None:
            self.GAME_MAP = [list(row) for row in GAME_MAP]
        else:
            pass  # TODO: нормальная мапа

    @property
    def debug(self):
        return self.vk is None

    @classmethod
    def _get_pos(cls, text: str):
        text = text.strip()
        try:
            x, y = text.split(':')
            x = ascii_uppercase.index(x.upper())
            y = int(y) - 1
            assert(0 <= x < cls.X)
            assert(0 <= y < cls.Y)
            return x, y
        except Exception as e:
            if cls.debug:
                print(e)
            return None

    @property
    def can_call(self):
        last = self.data['last_call']
        if last:
            return now() - last >= timedelta(seconds=self.recovery)
        return True

    def _render(self):
        if self.vk is None:
            return self._print()
        pass  # TODO: self.GAME_MAP processing

    def _print(self):
        os.system('cls')
        for i in self.GAME_MAP:
            print(*i)

    def execute(self, text):
        _pos = self._get_pos(text)
        if _pos is None or not self.can_call:
            return  # exit
        x, y = _pos
        tile = self.GAME_MAP[y][x]
        if tile in [EMPTY, CLOSE]:
            tile = EMPTY
        elif tile in TREASURES.keys():
            award, new_tile = TREASURES.get(tile)
            tile = new_tile
            self.data['score'] += award
        self.data['last_call'] = now()
        self.GAME_MAP[y][x] = tile
        self.save()
        self._render()


class GameShell(object):
    game = None

    def __init__(self):
        user, _ = VkUser.objects.using('old_bot').get_or_create(
            user_id=123
        )
        self.game = Game(user=user)

    def execute(self):
        txt = input()
        while txt != 'stop':
            self.game.execute(txt)
            txt = input()
