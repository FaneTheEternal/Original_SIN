import sys

import vk_api
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.exceptions import ApiError

from .bot_config import token
from .models import VkUser
from .chat_bot_texts import TEXTS

from .sections import Incoming, QuestRoute

COMMON_COMMANDS = [
    'Поступающим',
    'Расписание звонков',
    'Схема корпусов',
    'Общежития',
    'Стипендии',
    'Начать',
]

START_COMMAND = 'Начать'
HOME_COMMAND = 'Вернуться к боту'

SPECIAL_COMMANDS = [
    'Поступающим',
    'Тесты',
    'Задать вопрос специалисту',
]

ATTACHMENTS = {
    'Поступающим': 'photo-47825810_457309069',
    'Схема корпусов': [
        'photo-88277426_457239052',
        'photo-88277426_457239053',
        'photo-88277426_457239054',
        'photo-88277426_457239055',
        'photo-88277426_457239056',
        ],
    'Стипендии': [
        'photo-47825810_457309089',
        'photo-47825810_457309088',
        'photo-47825810_457309087',
        'photo-47825810_457309090',
        'photo-47825810_457309086',
        'photo-47825810_457309085',
    ]
}


def execute(data: dict):
    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()
    keyboard = VkKeyboard(one_time=True)

    obj = data['object']
    user_id = obj['from_id']
    user, created = VkUser.objects.get_or_create(
        user_id=user_id
    )
    message = ''

    text = obj['text']
    attachment = None

    incoming = Incoming()

    if created:
        return greeting(vk, user)

    elif text == HOME_COMMAND:
        return go_home(vk, user)

    elif user.status == VkUser.INCOMING:
        return incoming.execute(vk, user, text)

    elif user.status == VkUser.QUEST:
        return QuestRoute.execute(vk, user, text)

    elif user.status == VkUser.SPECIALIST:
        return  # None

    elif text in SPECIAL_COMMANDS:
        if text == 'Поступающим':
            message = TEXTS.get(text, ' ')
            keyboard = incoming.keyboard()
            user.status = VkUser.INCOMING
            user.save()

        elif text == 'Задать вопрос специалисту':
            user.status = VkUser.SPECIALIST
            user.save()
            keyboard = specialist_keyboard(one_time=False)
            message = TEXTS.get(text, ' ')

        elif text == 'Тесты':
            user.status = VkUser.QUEST
            user.save()
            return QuestRoute.execute(vk, user, text)

        else:
            return sleep()

    elif text in COMMON_COMMANDS:
        if text == START_COMMAND:
            return go_home(vk, user)
        keyboard = home_keyboard()
        message = TEXTS.get(text, ' ')
        attachment = ATTACHMENTS.get(text, None)

    else:
        return sleep(vk, user)

    try:
        vk.messages.send(
            peer_id=str(user_id),
            message=message,
            random_id=get_random_id(),
            keyboard=keyboard.get_keyboard(),
            attachment=attachment
        )
    except ApiError as pezdos:
        print('User_id: ', user_id, file=sys.stderr)
        print('Message: ', message, file=sys.stderr)
        print('Attachment: ', attachment, file=sys.stderr)
        print('Pezdos: ', pezdos, file=sys.stderr)


def home_keyboard(keyboard=None, one_time=True):
    if keyboard is None:
        keyboard = VkKeyboard(one_time=one_time)
    keyboard.add_button(
        'Поступающим', color=VkKeyboardColor.POSITIVE
    )

    keyboard.add_line()

    keyboard.add_button(
        'Расписание звонков', color=VkKeyboardColor.DEFAULT
    )
    keyboard.add_button(
        'Схема корпусов', color=VkKeyboardColor.DEFAULT
    )

    keyboard.add_line()

    keyboard.add_button(
        'Общежития', color=VkKeyboardColor.DEFAULT
    )
    keyboard.add_button(
        'Стипендии', color=VkKeyboardColor.DEFAULT
    )

    keyboard.add_line()

    keyboard.add_button(
        'Задать вопрос специалисту', color=VkKeyboardColor.DEFAULT
    )

    keyboard.add_line()

    keyboard.add_button(
        'Тесты', color=VkKeyboardColor.PRIMARY
    )
    return keyboard


def specialist_keyboard(keyboard=None, one_time=True):
    if keyboard is None:
        keyboard = VkKeyboard(one_time=one_time)
    keyboard.add_button(
        'Вернуться к боту', color=VkKeyboardColor.DEFAULT
    )
    return keyboard


def greeting(vk, user: VkUser):
    message = """
    Привет! Я робот Ульян. Чтобы перейти в раздел, выберите кнопку:
    """
    keyboard = home_keyboard()
    attachment = 'photo-47825810_457309091'
    vk.messages.send(
        peer_id=str(user.user_id),
        message=message,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
        attachment=attachment
    )


def sleep(vk, user: VkUser):
    if user.status != VkUser.SPECIALIST:
        user.status = VkUser.SPECIALIST
        user.save()
        message = TEXTS.get('sleep')
        keyboard = specialist_keyboard(one_time=False)
        vk.messages.send(
            peer_id=str(user.user_id),
            message=message,
            random_id=get_random_id(),
            keyboard=keyboard.get_keyboard()
        )


def go_home(vk, user: VkUser):
    keyboard = home_keyboard()
    message = 'Что вас интересует?'
    user.status = VkUser.HOME
    user.save()
    vk.messages.send(
        peer_id=str(user.user_id),
        message=message,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard()
    )


def fukk_go_back(vk, user: VkUser):
    if user.quest_profile.first():
        user.quest_profile.first().delete()
    if user.incoming_profile.first():
        user.incoming_profile.first().delete()
    return go_home(vk, user)
