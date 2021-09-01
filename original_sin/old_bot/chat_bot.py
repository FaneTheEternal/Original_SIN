import re

import vk_api
from django.conf import settings
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from core.utility import vk_send
from .models import VkUser
from .chat_bot_texts import TEXTS

from .sections import QuestRoute, Incoming

COMMON_COMMANDS = [
    'Схема корпусов',
    'Расписание',
    'Стипендии',
    'Общежития',
    'Поступающим',
    'Начать',
]

START_COMMAND = 'Начать'
HOME_COMMAND = 'Вернуться к боту'

SPECIAL_COMMANDS = [
    'Справочник контактов',
    'Тесты',
    'Задать вопрос специалисту',
]

ATTACHMENTS = {
    'Схема корпусов': [
        'photo-88277426_457239077',
        'photo-88277426_457239078',
        'photo-88277426_457239079',
        'photo-88277426_457239080',
        'photo-88277426_457239081',
    ],
    'Стипендии': [
        # 'photo-88277426_457239082',
        'photo-88277426_457239083',
        'photo-88277426_457239084',
        'photo-88277426_457239085',
        'photo-88277426_457239086',
        'photo-88277426_457239087',
        'photo-88277426_457239088',
        'photo-88277426_457239089',
        'photo-88277426_457239090',
        # 'photo-88277426_457239091',
    ]
}


def execute(data: dict):
    token = getattr(settings, 'CHUVSU_VK_TOKEN')

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

    if created:
        return greeting(vk, user)

    if text == START_COMMAND:
        return go_home(vk, user)

    elif text == HOME_COMMAND:
        return go_home(vk, user)

    elif user.status == VkUser.CONTACTS:
        return Contacts.execute(vk, user, text)

    elif user.status == VkUser.QUEST:
        return QuestRoute.execute(vk, user, text)

    elif user.status == VkUser.INCOMING:
        return Incoming.execute(vk, user, text)

    elif user.status == VkUser.SPECIALIST:
        return  # None

    elif text in SPECIAL_COMMANDS:
        if text == 'Задать вопрос специалисту':
            user.status = VkUser.SPECIALIST
            user.save()
            keyboard = specialist_keyboard(one_time=False)
            message = TEXTS.get(text, ' ')

        elif text == 'Тесты':
            user.status = VkUser.QUEST
            user.save()
            return QuestRoute.execute(vk, user, text)
        elif text == 'Справочник контактов':
            user.status = VkUser.CONTACTS
            user.save()
            keyboard = Contacts.keyboard()
            message = TEXTS.get(text, '-')
        elif text == 'Поступающим':
            user.status = VkUser.INCOMING
            user.save()
            keyboard = Incoming.keyboard()
            message = TEXTS.get(text, '-')

    elif text in COMMON_COMMANDS:
        keyboard = home_keyboard()
        message = TEXTS.get(text, ' ')
        attachment = ATTACHMENTS.get(text, None)

    else:
        return sleep(vk, user)

    vk_send(vk, user_id, message, keyboard, attachment)


def home_keyboard(keyboard=None, one_time=True):
    if keyboard is None:
        keyboard = VkKeyboard(one_time=one_time)
    keyboard.add_button(
        'Справочник контактов', color=VkKeyboardColor.DEFAULT
    )
    keyboard.add_button(
        'Схема корпусов', color=VkKeyboardColor.DEFAULT
    )
    keyboard.add_line()
    keyboard.add_button(
        'Расписание', color=VkKeyboardColor.DEFAULT
    )
    keyboard.add_button(
        'Стипендии', color=VkKeyboardColor.DEFAULT
    )
    keyboard.add_line()
    keyboard.add_button(
        'Общежития', color=VkKeyboardColor.DEFAULT
    )
    keyboard.add_button(
        'Поступающим', color=VkKeyboardColor.DEFAULT
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
        message=message.replace('    ', ''),
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard()
    )


def fukk_go_back(vk, user: VkUser):
    if user.quest_profile.first():
        user.quest_profile.first().delete()
    if user.incoming_profile.first():
        user.incoming_profile.first().delete()
    return go_home(vk, user)


class Contacts:
    WORDS = [
        'Факультеты',
        'Подразделения',
    ]

    BACK = 'Вернуться в основное меню'

    @classmethod
    def execute(cls, vk, user, text):
        message = ''
        attachment = None
        keyboard = None

        if text in cls.WORDS:
            message = cls.TEXTS.get(text, '-')
            user.set_default()
            keyboard = home_keyboard()

        elif text == cls.BACK:
            user.set_default()
            return go_home(vk, user)

        else:
            return sleep(vk, user)

        vk.messages.send(
            peer_id=str(user.user_id),
            message=re.sub(r'\n +', '\n', re.sub(' +', ' ', message)),
            random_id=get_random_id(),
            keyboard=keyboard.get_keyboard(),
            attachment=attachment
        )

    @classmethod
    def keyboard(cls, keyboard=None, one_time=True):
        if keyboard is None:
            keyboard = VkKeyboard(one_time=one_time)

        NEW_LINE = [i for i in range(len(cls.WORDS)) if i % 2 == 1]
        for i in range(len(cls.WORDS)):
            keyboard.add_button(
                cls.WORDS[i],
                color=VkKeyboardColor.DEFAULT
            )
            if i in NEW_LINE:
                keyboard.add_line()

        keyboard.add_button(
            cls.BACK,
            color=VkKeyboardColor.NEGATIVE
        )

        return keyboard

    TEXTS = {
        'Факультеты': """
            Историко-географический факультет
            Декан – Широков Олег Николаевич
            Деканат:  ул. Университетская, 38, учеб.корп. № 1, каб. 1-501, тел. 45-26-53 (доб. 3301), Geo_his@chuvsu.ru
            
            Машиностроительный факультет
            Декан – Гартфельдер Виктор Адольфович
            Деканат:  ул. С. Михайлова, 3, корп. «Т»: очное отделение – каб.Т-214, тел. 45-21-93; заочное отделение – каб.Т-216, тел. 45-38-08 (доб.7102), msf68@bk.ru 
            
            Медицинский факультет
            Декан – Диомидова Валентина Николаевна
            Деканат:  Московский пр., 45, корп. «М», специальность «Лечебное дело» - каб.М-117, тел. 45-17-39; специальность «Педиатрия» - каб. М-115, тел. 452079; специальность «Стоматология» - каб. М-119, тел.45-39-68, mfchgu@gmail.com ; lechfac@mail.ru 
            
            Строительный факультет
            Декан – Плотников Алексей Николаевич
            Деканат:  пр. Ленина, 6, корп. «Н»: очное отделение - каб. Н-208, тел. 62-45-96 (доб. 6101), заочное отделение – каб. Н-210, тел.62-47-95 (доб.6103), strf@chuvsu.ru
            
            Факультет иностранных языков
            Декан – Емельянова Маргарита Валентиновна
            Деканат: ул. Университетская, 38, учеб.корп. № 3, каб. 3-306, тел. 45-15-01 (доб. 3501) dekin@chuvsu.ru 
            
            Факультет информатики и вычислительной техники
            Декан – Щипцова Анна Владимировна
            Деканат:  Московский пр., 15, корп. «Б», каб. Б-106, тел. 58-01-45, fivt@chuvsu.ru
            
            Факультет искусств
            Декан – Яклашкин Морис Николаевич
            Деканат:  ул. Университетская, 38, учеб.корп. № 3, каб. 3-105, тел. 45-80-83 (доб. 3251), isfak@chuvsu.ru
            
            Факультет русской и чувашской филологии и журналистики:
            Декан – Иванова Алена Михайловна
            Деканат: ул. Университетская, д. 38, учеб.корп. № 1: русская филология – каб.1-401, тел. 45-93-90 (доб.3151),filolog@chuvsu.ru; чувашская филология – каб. 1-409, тел. 45-03-37 (доб.3101), chuvfil@chuvsu.ru; журналистика – каб. 1-437, тел. 45-81-20 (доб. 3201), jourfak@chuvsu.ru.
            
            Экономический факультет
            Декан – Морозова Наталия Витальевна
            Деканат:  Московский пр., 29, корп. «Е», очное отделение - каб.204Б, тел. 58-31-68 (доб. 4101); заочное отделение - каб. Е-204А, тел.58-06-90, dekd@chuvsu.ru
            
            Юридический факультет
            Декан – Иванова Елена Витальевна
            Деканат:  ул. Университетская, 38, учеб.корп. №  1, очное отделение - каб. 1-214, тел. 45-01-15, uf-decanat@yandex.ru ; заочное отделение - каб. 3-406, тел.40-01-45, vech-dekanat@mail.ru
            
            Факультет прикладной математики, физики и информационных технологий 
            Декан – Иваницкий Александр Юрьевич
            Деканат:  ул. Университетская, 38, учеб.корп. № 1, каб. 1-302, тел.  45-56-00 (доб. 3601), phiz-matdek@mail.ru
            
            Факультет управления и социальных технологий 
            Декан – Семенов Владислав Львович
            Деканат:  Московский пр., 19, корп. «О», каб. О-112, тел. 45-20-31 (доб. 2401), fuip@chuvsu.ru
            
            Химико-фармацевтический факультет
            Декан – Насакин Олег Евгеньевич
            Деканат:  Московский пр., 19, корп. «О», каб. О-312, тел. 45-24-68 (доб. 2301), chemdec@chuvsu.ru 
            
            Факультет энергетики и электротехники
            Декан – Ковалев Владимир Геннадьевич
            Деканат:  Московский пр., 15, корп. «Г»: очное отделение - каб. Г-307, тел. 58-46-00 (доб. 2501), заочное отделение – каб. Г-308, тел. 58-36-02 (доб.2601), etf@chuvsu.ru
            
            Факультет радиоэлектроники и автоматики 
            Декан – Охоткин Григорий Петрович 
            Деканат: Московский пр., 15, корп. «Г», каб. Г-413, тел. 58-12-59 (доб. 2701), frte@chuvsu.ru
        """,
        'Подразделения': """
            Студенческий совет
            Московский пр., 15, главный корпус, 1 этаж, правое крыло, каб.К-103. Тел. 8-927-667-09-27 (37-09-27), studsovet_chgu@mail.ru 
            
            Профком обучающихся
            Московский пр., 15, главный корпус, 1 этаж, левое крыло, каб. И-108. Пн-Пт 08.00-17.00, обед 12.00-13.00. Тел. 58-50-98, profkomchgu@gmail.com
            
            Отдел кадров студентов 
            Московский пр., 15, главный корпус , 1 этаж, центр, каб. Г-111, тел. 45-80-08 (доб. 2049). Пн-Пт 08.00-17.00, обед 12.00-13.00, технический перерыв 10.00-11.00.
            
            Расчетный отдел студентов 
            Московский пр., 15, главный корпус, 2 этаж, правое крыло, каб.К-211. Пн-Пт 08.00-17.00, обед 12.00-13.00. Тел. 58-34-87 (доб.2063).
            
            Касса 
            Московский пр., 15, главный корпус, 2 этаж, правое крыло, каб. К-202. Пн-Пт 08.00-11.30, 14.00-16.30.
            
            Отдел по работе с обучающимися на договорной основе (отдел маркетинга)
            Московский пр., 15, главный корпус, 1 этаж, правое крыло, каб. Г-120. Пн-Пт 08.00-17.00, обед 12.00-13.00. Тел. 58-11-46, 45-26-91 (доб.2067), market120@chuvsu.ru .
            
            Второй отдел (военно-учетный стол студентов) 
            Московский пр.,  15, главный корпус, 1 этаж, центр, каб. Г-106. Пн-Пт 08.00-17.00, обед 12.00-13.00.
            Тел. 45-01-41 (доб.2084).
            
            Общий отдел (канцелярия)
            Московский пр.,  15, главный корпус, 1 этаж, центр, каб. Г-107. Пн-Пт 08.00-17.00, обед 12.00-13.00.
            Тел. 45-01-41 (доб.2051).
            
            Отдел социального развития 
            Московский пр., 15, главный корпус, 1 этаж, левое крыло, каб. И-104а. Пн-Пт 08.00-17.00, обед 12.00-13.00. Тел. 58-59-77 
            
            Студенческое научное общество
            Московский пр., 15, главный корпус, 4 этаж, центр, каб. Г-410. Пн-Пт 08.00-17.00, обед 12.00-13.00. Тел. 45-01-41, доб. 20-37, snochgu@gmail.com
            
            Администрация Студенческого городка 
            Московский пр., 19/3, общежитие №7. Пн-Пт 08.00-17.00, обед 12.00-13.00. Тел. 45-48-35 (доб. 2450). Паспортный стол – тел. 45-48-35 (доб. 2452) 
            
            Центр по работе с одаренной молодежью
            Ул. Университетская, 38, учеб.корп. №1, каб. 1- 319. Пн-Пт 08.00-17.00, обед 12.00-13.00. Тел. 45-00-91.
            
            Центр дополнительного образования
            Московский пр., 15, главный корпус, 2 этаж, правое крыло, каб. К-204. Пн-Пт 08.00-17.00, обед 12.00-13.00. Тел. 58-45-74, cdo_chuvsu@bk.ru
            
            Автошкола ЧГУ
            Московский пр., 15, корпус «З», каб. 207. Пн-Пт 08.00-17.00, обед 12.00-13.00.Тел. 8-919-977-32-50.
            
            Студия ГТО
            Московский пр., 19/2, общежитие № 6, тел. 8-987-679-42-78 
        """
    }
