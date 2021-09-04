import inspect
import json
import logging
import os
import re
import sys
from pathlib import Path

import telebot
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from telebot import types

from chuvsu.models import BotProfile2
from core.utility import func_once

logger = logging.getLogger(__name__)

token = getattr(settings, 'CHUVSUGUIDE_BOT_TOKEN', None)
if token:
    bot = telebot.TeleBot(token)
    domain = getattr(settings, 'ALLOWED_HOSTS')[0]  # awhile crutch
    try:
        bot.set_webhook(url=f'https://{domain}/chuvsu/chuvsuguide_bot')
    except Exception as e:
        import traceback

        logger.error(e)
        logger.error(traceback.format_exc())


@csrf_exempt
def index(request):
    if request.method == 'POST':
        try:
            message = json.loads(request.body)['message']
            StartChat.execute(message)
        except Exception as e:
            import traceback
            logger.error(traceback.format_exc())
    return HttpResponse('ok', content_type="text/plain")


BASE_IMAGE_PATH = Path(settings.BASE_DIR).joinpath('chuvsu', 'static', 'chuvsu')


class ChatBase:
    BACK = 'Назад'

    OPTIONS = []

    TEXTS = {}

    SINKING = {}

    GREETING = ''

    PHOTOS = {}

    @classmethod
    def get_user(cls, message):
        return BotProfile2.objects.get(user_guid=message['chat']['id'])

    @classmethod
    def execute(cls, message, join=False):
        user = cls.get_user(message)
        if join:
            user.set_step(cls.__name__)
            return cls.default(message)
        text = message['text']
        if text == cls.BACK:
            chat = user.get_back(all_chats())
            if chat:
                return chat.execute(message, join=True)
        if text in cls.SINKING:
            chat = cls.SINKING[text]
            return chat.execute(message, join=True)
        if text in cls.TEXTS:
            return cls.send(message, cls.TEXTS[text])
        return cls.default(message)

    @classmethod
    def default(cls, message):
        cls.send(message, cls.GREETING)

    @classmethod
    def keyboard(cls):
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        if cls.OPTIONS:
            markup.add(*cls.OPTIONS, row_width=2)
        markup.add(cls.BACK)
        return markup

    @classmethod
    def send_photo(cls, message, photo):
        bot.send_chat_action(message['chat']['id'], 'upload_photo')
        img = open(BASE_IMAGE_PATH.joinpath(photo), 'rb')
        bot.send_photo(message['chat']['id'], img)
        img.close()

    @classmethod
    def send(cls, message, text: str):
        if message['text'] in cls.PHOTOS:
            cls.send_photo(message, cls.PHOTOS[message['text']])
        text = text.strip()
        text = re.sub('\n +', '\n', text)
        bot.send_message(
            message["chat"]["id"],
            text,
            reply_markup=cls.keyboard()
        )


class QuestionOrSuggestionChat(ChatBase):
    GREETING = 'Чем тебе помочь?'


class FindHousingChat(ChatBase):
    GREETING = 'Выбери корпус, о котором тебе нужна информация'

    OPTIONS = [
        'Главный корпус',
        'Корпус "Т", машиностроительный',
        'Корпус "Е", экономический',
        'Корпус "О", химфак, ФУиСТ',
        'Корпус "Н", строительный',
        'Корпуса "Л", "М", "П", "С", медицинский',
        'Новый корпус',
    ]

    TEXTS = {
        'Главный корпус': 'NotImplemented',
        'Корпус "Т", машиностроительный': 'NotImplemented',
        'Корпус "Е", экономический': 'NotImplemented',
        'Корпус "О", химфак, ФУиСТ': 'NotImplemented',
        'Корпус "Н", строительный': 'NotImplemented',
        'Корпуса "Л", "М", "П", "С", медицинский': 'NotImplemented',
        'Новый корпус': 'NotImplemented',
    }


class StructuralUnitsChat(ChatBase):
    GREETING = """
        Это очень важные объединения нашего университета. 
        Представители этих структур есть на каждом факультете, и ты смело можешь обращаться к ним с вопросиками. 
        Ознакомься с информацией о каждом из них, чтобы знать к кому по какому делу обращаться.
    """

    OPTIONS = [
        'Профком',
        'Студсовет',
        'Спортивный клуб',
        'СНО',
        'Дворец культуры ЧГУ',
    ]

    PHOTOS = {
        'Профком': 'profcom.jpg',
        'Студсовет': 'studsovet.jpg',
        'Спортивный клуб': 'sport_club.jpg',
        'СНО': 'sno.jpg',
        'Дворец культуры ЧГУ': 'dk_chgu.jpg',
    }

    TEXTS = {
        'Профком': """
            Защищает права студентов и предоставляет социальные гарантии членам профсоюза. 
            Профком помогает обучающимся в разрешении сложных социальных и материальных вопросов, 
            лоббирует интересы студенчества перед администрацией вуза и на других уровнях. 
            Обращайся к профоргу своего факультета или приходи по адресу Московский проспект, д.15, каб. И-108.
            Группа ВК – https://vk.com/profkom21
            Защитник прав студентов aka председатель профкома – Афиногенов Никита Игоревич
            Профорг твоего факультета – https://vk.com/@profkom21-proforgi-chgu
        """,
        'Студсовет': """
            Это орган студенческого самоуправления вуза. 
            Ребята из студсовета создают общественно полезные проекты с конкретными целями и задачами, 
            находят пути их решения и всегда достигают желаемых результатов. 
            По вопросам обращайся к председателю студсовета своего факультета или приходи по адресу Московский проспект, 
            д.15, каб. К-103
            Группа ВК – https://vk.com/studsovetchgu
            Председатель студсовета – Семенова Ольга Алексеевна
            Председатель студсовета на твоем факультете – в разделе «Контакты» группы ВК
        """,
        'Спортивный клуб': """
            Традиционно в университете проводятся различные спортивные мероприятия и эстафеты для студентов и преподавателей. 
            Команды и спортсмены университета успешно выступают в различных соревнованиях республиканского, всероссийского и международного уровня. 
            Если ты поддерживаешь здоровый образ жизни и занимаешься спортом, 
            обращайся за информацией по спортивным мероприятиям в Спортивный клуб ЧувГУ им. Ульянова. 
            Он находится по адресу Московский проспект, д.15, каб. К-303а.
            Группа ВК – https://vk.com/sport_chgu
            Председатель ССК – Симонова Ольга Юрьевна
        """,
        'СНО': """
            Это добровольное объединение студентов ЧувГУ, которое занимается организацией и проведением научно-практических конференций, «круглых столов», олимпиад, квестов и других не менее интересных научных мероприятий. СНО можно найти по адресу Московский проспект, д.15, каб. Г-410.
            Группа ВК – https://vk.com/snochuvsu
            Научный руководитель СНО ЧувГУ – Матюшин Петр Николаевич
            Председатель СНО ЧувГУ – Шварнуков Алексей Валерьевич
            Председатель СНО твоего факультета – в разделе «Контакты» группы ВК
        """,
        'Дворец культуры ЧГУ': """
            Это не просто современная и круто оснащенная площадка, на которой проводятся концерты, спектакли, форумы, мастер-классы. Это Центр молодежной культуры Чувашии. На этой сцене, кстати, пела и танцевала Ольга Бузова. На этой же сцене можешь блистать и ты. По вопросам участия в творческой жизни университета обращайся к культоргу своего факультета.
            Дворец Культуры находится по адресу ул. Университетская, д. 38.
            Группа ВК – https://vk.com/dkchgu
            Директор ДК ЧГУ – Заворзаева Анна Васильевна
            Культорг твоего факультета – https://vk.com/@dkchgu-kultorgi-dk-chgu
        """,
    }


class SportsAndTourismChat(ChatBase):
    GREETING = """
        Мы заботимся о том, чтобы наши студенты были самыми здоровыми и спортивными. 
        Смотри, что у нас для тебя есть
    """

    OPTIONS = [
        'Спортивные секции',
        'Студия ГТО',
        'Турклуб ЧувГУ',
    ]

    PHOTOS = {
        'Спортивные секции': 'sport_section.jpg',
        'Студия ГТО': 'gto.jpg',
        'Турклуб ЧувГУ': 'tour_club.jpg',
    }

    TEXTS = {
        'Спортивные секции': """
            Спортивный клуб ЧувГУ скоро составит и выложит расписание спортивных секций на 2021-2022 учебный год. 
            Дисциплин на выбор очень много: от шашек до мини-футбола. 
            Так что идем прокачивать не только тело, но и мозги. 
        """,
        'Студия ГТО': """
            Здесь профессионально готовят для сдачи норм ГТО и к следующему лету. 
            Групповые занятия, тренажерный зал и персональные тренировки – выбирай то, что тебе по душе. 
            Иногда здесь проводятся бесплатные занятия и дни открытых дверей, но и абонемент на месяц стоит, примерно, как 7 двойных чизбургеров из Мака.
            Адрес: Московский пр-т, 19 корп. 2, Чебоксары
        """,
        'Турклуб ЧувГУ': """
            Очень полезно ходить пешком. Представь: идёшь, веселишься в классной компании и вдруг ты в горах. 
            Такие фокусы тебе покажут наши ребята из турклуба ЧувГУ: снег, дождь, тяжелые рюкзаки - все это стоит одной тёплой дружной компании. Обычно в начале учебного года ребята проводят день открытых дверей, куда приглашают всех желающих присоединиться. 
        """,
    }


class CreativityAndHobbiesChat(ChatBase):
    GREETING = """
        Здесь ребята делают классные вещи. 
        Ты можешь просто следить за их деятельностью, ведь каждое направление делает огромный вклад в развитие универа. 
        Но ты также можешь стать их частью.
    """

    OPTIONS = [
        'Волонтерский центр ЧувГУ',
        'Студии ДК ЧГУ',
        'Киберклуб ЧувГУ',
        'Медиа-центр ЧГУ NEWS',
    ]

    PHOTOS = {
        'Волонтерский центр ЧувГУ': 'volonter.jpg',
        'Студии ДК ЧГУ': 'stud_dk_chuvsu.jpg',
        'Киберклуб ЧувГУ': 'e-sport.jpg',
        'Медиа-центр ЧГУ NEWS': 'news.jpg',
    }

    TEXTS = {
        'Волонтерский центр ЧувГУ': """
            Входит в структуру Студенческого совета ЧувГУ и включает в себя 7 направлений деятельности. 
            Для ребят, желающих присоединиться, двери всегда открыты. 
            Здесь ты найдешь много новых друзей и поможешь сделать этот мир еще ярче и добрее.
            https://vk.com/vc_chgu
        """,
        'Студии ДК ЧГУ': """
            Входит в структуру Студенческого совета ЧувГУ и включает в себя 7 направлений деятельности.  
            Для ребят, желающих присоединиться, двери всегда открыты. 
            Здесь ты найдешь много новых друзей и поможешь сделать этот мир еще ярче и добрее.
            https://vk.com/vc_chgu
        """,
        'Киберклуб ЧувГУ': """
            Студенческое объединение, являющееся структурным подразделением Профкома обучающихся, созданное с целью развития и популяризации киберспорта в университете и Чувашии в целом. Ребята из команды проводят классные мероприятия, соревнования и мастер-классы, на которые приглашают всех заинтересованных в теме ребят.
        """,
        'Медиа-центр ЧГУ NEWS': """
            Росточек профкома обучающихся ЧувГУ, который в 2020 году стал самостоятельной структурой нашего университета. Ребята вещают со всех событий университета: готовят фотоотчеты и видеоролики, где ты сможешь найти себя, если не постесняешься попозировать. В группе ВК они также публикуют всякие молодежные штуки, мемы и все то, что связано со студенчеством.
            Кстати, каждую осень ЧГУ NEWS объявляют набор в свою команду, в котором может поучаствовать любой желающий. Подписывайся, следи за обновлениями и чувствуй себя как дома. 
            https://vk.com/chgunews
        """,
    }


class AdditionalEducationChat(ChatBase):
    GREETING = """
        Приобретай важные навыки, которые пригодятся тебе во взрослой жизни, не выходя из универа.
    """

    OPTIONS = [
        'Бизнес-инкубатор',
        'Автошкола',
    ]

    TEXTS = {
        'Бизнес-инкубатор': """
            Структурное подразделение университета, которое поможет тебе получить опыт предпринимательства. 
            Наставники помогут тебе разобраться в бизнес-сфере, а также окажут поддержку в привлечении финансирования на реализацию твоих идей.
        """,
        'Автошкола': """
            У нас есть своя автошкола, и она находится прямо на территории университета. 
            Это не бесплатно, но студенты и преподаватели могут получить дополнительную скидку на обучение. 
            А если придешь с другом, еще и получишь приятные бонусы.
            https://vk.com/autochgu21
        """,
    }


class HealthChat(ChatBase):
    GREETING = """
        Никаких стрессов после сессии. 
        Мы готовы поправить твое здоровье прямо в университете.
    """

    OPTIONS = [
        'Санаторий-профилакторий ЧувГУ',
        'Вакцинация',
    ]

    TEXTS = {
        'Санаторий-профилакторий ЧувГУ': """
            Это самое вайбовое место в нашем универе. 
            Здесь можно бесплатно жить целую смену (21 день), кушать 3 раза в день, ходить на оздоровительные процедуры и укреплять иммунитет витаминками, которые тоже выдают бесплатно. 
            Возможно, что из-за пандемии смены пока будут проходить без заселения. 
            О начале новой смены мы рассказываем в TG-канале и группе профкома обучающихся ЧувГУ.
        """,
        'Вакцинация': """
            В нашем университете действует прививочный пункт для всех сотрудников и студентов. 
            Нужно только записаться по телефону 8-961-339-19-03 или написать на sanprof@chuvsu.ru.
            Вакцинацию проходит в Новом корпусе (ул. Университетская, д. 38, каб. I-103 и I-105).
        """,
    }


class RecreationAndEntertainmentChat(ChatBase):
    GREETING = """
        Легкий чилл учебе не помешает. 
        Смотри, как можно весело провести время после пар.
    """

    OPTIONS = [
        'Научная библиотека',
        'Коворкинг',
        'Клуб настольных игр',
    ]

    TEXTS = {
        'Научная библиотека': """
            Здесь можно найти не только учебные материалы для подготовки к экзаменам, но и художественную литературу. 
            Стеллажи постоянно пополняются новыми книгами, и здесь всегда рады новым читателям. 
            Университетская 38, корпус №3
        """,
        'Коворкинг': """
            Целая аудитория с разноцветными диванчиками, компьютерами и столами. 
            Здесь можно и поработать, и просто почиллить после пар. 
            Университетская 38, библиотечный корпус, 5 этаж
        """,
        'Клуб настольных игр': """
            Когда все студенты уходят с пар, просыпается мафия. 
            И не только мафия, другие настолки мы тоже любим. 
            Вступай в группу, чтобы не пропустить игры на своём факультете. 
            Это отличный способ расслабиться после пар и найти новых друзей. 
            О времени и месте проведения организаторы сообщают заранее.
            https://vk.com/club199661053
        """,
    }


class ExtracurricularLifeChat(ChatBase):
    GREETING = 'О чем тебе рассказать?'

    OPTIONS = [
        'Структурные подразделения',
        'Спорт и туризм',
        'Творчество и увлечения',
        'Дополнительное образование',
        'Здоровье',
        'Отдых и развлечения',
        'Подписаться на TG канал ЧувГУ',
    ]

    TEXTS = {
        'Подписаться на TG канал ЧувГУ': """
            У нас в университете много возможностей. 
            Мы все рассказываем в нашем TG-канале @chuvsu21. 
            Подпишись, чтобы не пропустить ничего интересного
        """,
    }

    SINKING = {
        'Структурные подразделения': StructuralUnitsChat,
        'Спорт и туризм': SportsAndTourismChat,
        'Творчество и увлечения': CreativityAndHobbiesChat,
        'Дополнительное образование': AdditionalEducationChat,
        'Здоровье': HealthChat,
        'Отдых и развлечения': RecreationAndEntertainmentChat,
    }


class StartChat(ChatBase):
    GREETING = """
        Привет! Этот бот-помощник поможет тебе познакомиться с нашим университетом и его возможностями. 
        Расскажем все самое важное: где покушать и как скрасить свою рутину внеучебной деятельностью.
        Пс, полезно будет, даже если ты не первак.
    """

    SPECIAL = 'У меня есть вопрос или предложение'

    OPTIONS = [
        'Найти корпус',
        'Внеучебная жизнь',
        SPECIAL,
    ]

    SINKING = {
        'Найти корпус': FindHousingChat,
        'Внеучебная жизнь': ExtracurricularLifeChat,
        SPECIAL: QuestionOrSuggestionChat,
    }

    @classmethod
    def get_user(cls, message):
        return BotProfile2.objects.get_or_create(
            dict(
                user_guid=message['chat']['id'],
                current=cls.__name__,
            ),
            user_guid=message['chat']['id']
        )[0]

    @classmethod
    def execute(cls, message, join=False):
        user = cls.get_user(message)
        join = join or not bool(user.current)
        if join:
            return super(StartChat, cls).execute(message, join=join)
        chat = all_chats()[user.current]
        if chat is not cls:
            return chat.execute(message)
        return super(StartChat, cls).execute(message)

    @classmethod
    def keyboard(cls):
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        if cls.OPTIONS:
            markup.add(*cls.OPTIONS, row_width=2)
        return markup


@func_once
def all_chats():
    chats = dict()
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj) and issubclass(obj, ChatBase):
            chats[name] = obj
    return chats
