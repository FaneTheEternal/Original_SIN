import logging
import re

from vk_api.keyboard import VkKeyboard
from vk_api.utils import get_random_id

logger = logging.getLogger(__name__)


def func_once(func):
    """A decorator that runs a function only once."""
    attrname = '_once_result'

    def decorated(*args, **kwargs):
        if not hasattr(decorated, attrname):
            setattr(decorated, attrname, func(*args, **kwargs))

        return getattr(decorated, attrname)

    return decorated


def method_once(method):
    """A decorator that runs a method only once."""
    attrname = f'_{id(method)}_once_result'

    def decorated(self, *args, **kwargs):
        try:
            return getattr(self, attrname)
        except AttributeError:
            setattr(self, attrname, method(self, *args, **kwargs))
            return getattr(self, attrname)

    return decorated


def my_import(name):
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


def construct(*objects, **kwargs):
    result = []
    for o in objects:
        print(o, kwargs)
        try:
            result.append(o(**kwargs))
        except Exception as e:
            print(e)
    return result


def get_filename(name):
    if '/' in name:
        name = name[name.rfind('/') + 1:]
    return name


def vk_send(vk, user_id, message: str, keyboard, attachment=None):
    if isinstance(keyboard, VkKeyboard):
        keyboard = keyboard.get_keyboard()
    message = message.strip()
    message = re.sub(r' +', ' ', message)
    message = message.replace('\n ', '\n')
    # if isinstance(attachment, (list, tuple, set)):
    #     attachment = ','.join(attachment)
    return vk.messages.send(
        peer_id=str(user_id),
        message=message,
        random_id=get_random_id(),
        keyboard=keyboard,
        attachment=attachment
    )
