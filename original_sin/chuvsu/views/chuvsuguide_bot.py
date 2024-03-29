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
            reply_markup=cls.keyboard(),
            parse_mode='HTML',
        )


class QuestionOrSuggestionChat(ChatBase):
    GREETING = """
        Ты можешь оставить здесь анонимные предложения для университета и задать свои вопросы, 
        на которые мы ответим в нашем Telegram-канале
        <a href="https://docs.google.com/forms/d/e/1FAIpQLSdzfL4HEeZM6vW7dMqOmGwIIL-PTJRNgomnRJHTPSi8ebapyA/viewform">Вопросы и предложения</a>
    """


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
        'Главный корпус': """
            <i>Московский проспект, 15</i>
            Здесь, в основном, проходят пары у студентов ИВТ, РЭА и ЭиЭТ. В главном корпусе также находятся важные административные структуры.
            Всего на этой территории расположено 9 корпусов:
            А - административный корпус. Там есть зал заседания, в котором обычно проходят серьёзные деловые встречи, собрания или награждения.
            Г, К, И - Здесь расположен основной вход в главный корпус. Корпуса К и И в местном лексиконе больше известны как «крыло» корпуса Г: слева - крыло «И», справа - крыло «К» (относительно входа).
            Б, В, Д - учебные корпуса
            Ж - интернет-центр
            З - учебный корпус и автошкола

            <i>Контакты деканатов:</i>
            Факультет энергетики и электротехники
            Декан – Ковалев Владимир Геннадьевич
            Деканат: очное – каб. Г-307, тел. 58-46-00 (доб. 2501), 
            заочное – каб. Г-308, тел. 58-36-02 (доб.2601), etf@chuvsu.ru
            
            Факультет радиоэлектроники и автоматики
            Декан – Охоткин Григорий Петрович
            Деканат: каб. Г-413, тел. 58-12-59 (доб. 2701), frte@chuvsu.ru
            
            Факультет информатики и вычислительной техники
            Декан – Щипцова Анна Владимировна
            Деканат: корп. «Б», каб. Б-106, тел. 58-01-45, fivt@chuvsu.ru
        """,
        'Корпус "Т", машиностроительный': """
            <i>ул. Спиридона Михайлова, 3</i>
            Это корпус машиностроительного факультета. Здесь также расположены Центр молодежного инновационного творчества, Инжиниринговый центр.
            
            <i>Контакты деканата:</i>
            Декан – Гартфельдер Виктор Адольфович
            Деканат: очное – каб.Т-214, тел. 45-21-93; 
            заочное – каб.Т-216, тел. 45-38-08 (доб.7102), 
            msf68@bk.ru
        """,
        'Корпус "Е", экономический': """
            <i>Московский проспект, 29</i>
            Здесь проходят пары у студентов экономического факультета. В корпусе также находятся Точка кипения и Бизнес-инкубатор.
            
            <i>Контакты деканата:</i>
            Декан – Морозова Наталия Витальевна
            Деканат: очное – каб.204Б, тел. 58-31-68 (доб. 4101); 
            заочное - каб. Е-204А, тел.58-06-90, dekd@chuvsu.ru
        """,
        'Корпус "О", химфак, ФУиСТ': """
            <i>Московский проспект,19</i>
            Соседствует с главным корпусом. Здесь учится химфак и ФУиСТ.
            
            <i>Контакты деканата:</i>
            Факультет управления и социальных технологий
            Декан – Семенов Владислав Львович
            Деканат: каб. О-112, тел. 45-20-31 (доб. 2401), fuip@chuvsu.ru
            
            Химико-фармацевтический факультет
            Декан – Насакин Олег Евгеньевич
            Деканат: каб. О-312, тел. 45-24-68 (доб. 2301), chemdec@chuvsu.ru
        """,
        'Корпус "Н", строительный': """
            <i>Проспект Ленина, 6</i>
            Здесь учатся студенты строительного факультета.

            <i>Контакты деканата:</i>
            Декан – Плотников Алексей Николаевич
            Деканат: очное – каб. Н-208, тел. 62-45-96 (доб. 6101), 
            заочное – каб. Н-210, тел.62-47-95 (доб.6103), 
            strf@chuvsu.ru
        """,
        'Корпуса "Л", "М", "П", "С", медицинский': """
            Корпус «М» – Московский проспект, 45
            Корпус «Л» – Пирогова, 5
            Корпус «С» – Пирогова, 3
            Корпус «П» – Пирогова, 7
            Медиков всегда было очень много, поэтому у них есть 4 учебных корпуса. Все они расположены рядом друг с другом. Кстати, именно медики в прошлом году заселились в новое отреставрированное общежитие №2.
            
            <i>Контакты деканата:</i> 
            Декан – Диомидова Валентина Николаевна
            Деканат: специальность «Лечебное дело» - каб.М-117, тел. 45-17-39; 
            специальность «Педиатрия» – каб. М-115, тел. 452079; 
            специальность «Стоматология» – каб. М-119, тел.45-39-68, 
            mfchgu@gmail.com ; lechfac@mail.ru
        """,
        'Новый корпус': """
            <i>ул. Университетская, 38</i>
            Здесь проходят пары у студентов ИГФ, юрфака, РиЧФиЖ, ФПМФиИТ, факультета иностранных языков и факультета искусств.
            На территории «нового корпуса» разместились учебные корпуса №1, №2 и №3, а также Дворец Культуры ЧГУ, Научная библиотека и учебно-спортивный комплекс. На этой же территории строится бассейн ЧувГУ.
            
            <i>Контакты деканата:</i>
            ИГФ
            Декан – Широков Олег Николаевич
            Деканат: учеб.корп. № 1, каб. 1-501, тел. 45-26-53 (доб. 3301), 
            Geo_his@chuvsu.ru
            
            Факультет иностранных языков
            Декан – Емельянова Маргарита Валентиновна
            Деканат: учеб.корп. № 3, каб. 3-306, тел. 45-15-01 (доб. 3501) 
            dekin@chuvsu.ru
            
            Факультет искусств
            Декан – Яклашкин Морис Николаевич
            Деканат: учеб.корп. № 3, каб. 3-105, тел. 45-80-83 (доб. 3251),
             isfak@chuvsu.ru
            
            РиЧФиЖ:
            Декан – Иванова Алена Михайловна
            Деканат: учеб.корп. № 1: русская филология – каб.1-401, тел. 45-93-90 (доб.3151),filolog@chuvsu.ru; чувашская филология – каб. 1-409, тел. 45-03-37 (доб.3101), chuvfil@chuvsu.ru; журналистика – каб. 1-437, тел. 45-81-20 (доб. 3201), jourfak@chuvsu.ru.
            
            Юридический факультет
            Декан – Иванова Елена Витальевна
            Деканат: учеб.корп. № 1, очное - каб. 1-214, тел. 45-01-15, uf-decanat@yandex.ru ; 
            заочное - каб. 3-406, тел.40-01-45, vech-dekanat@mail.ru
            
            ФПМФиИТ
            Декан – Иваницкий Александр Юрьевич
            Деканат: учеб.корп. № 1, каб. 1-302, тел. 45-56-00 (доб. 3601), phiz-matdek@mail.ru
        """,
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
            <b>Группа ВК</b> – https://vk.com/profkom21
            <b>Защитник прав студентов aka председатель профкома</b> – Афиногенов Никита Игоревич
            <b>Профорг твоего факультета</b> – https://vk.com/@profkom21-proforgi-chgu
        """,
        'Студсовет': """
            Это орган студенческого самоуправления вуза. 
            Ребята из студсовета создают общественно полезные проекты с конкретными целями и задачами, 
            находят пути их решения и всегда достигают желаемых результатов. 
            По вопросам обращайся к председателю студсовета своего факультета или приходи по адресу Московский проспект, 
            д.15, каб. К-103
            <b>Группа ВК</b> – https://vk.com/studsovetchgu
            <b>Председатель студсовета</b> – Семенова Ольга Алексеевна
            <b>Председатель студсовета на твоем факультете</b> – в разделе «Контакты» группы ВК
        """,
        'Спортивный клуб': """
            Традиционно в университете проводятся различные спортивные мероприятия и эстафеты для студентов и преподавателей. 
            Команды и спортсмены университета успешно выступают в различных соревнованиях республиканского, всероссийского и международного уровня. 
            Если ты поддерживаешь здоровый образ жизни и занимаешься спортом, 
            обращайся за информацией по спортивным мероприятиям в Спортивный клуб ЧувГУ им. Ульянова. 
            Он находится по адресу Московский проспект, д.15, каб. К-303а.
            <b>Группа ВК</b> – https://vk.com/sport_chgu
            <b>Председатель ССК</b> – Симонова Ольга Юрьевна
        """,
        'СНО': """
            Это добровольное объединение студентов ЧувГУ, которое занимается организацией и проведением научно-практических конференций, «круглых столов», олимпиад, квестов и других не менее интересных научных мероприятий. СНО можно найти по адресу Московский проспект, д.15, каб. Г-410.
            <b>Группа ВК</b> – https://vk.com/snochuvsu
            <b>Научный руководитель СНО ЧувГУ</b> – Матюшин Петр Николаевич
            <b>Председатель СНО ЧувГУ</b> – Шварнуков Алексей Валерьевич
            <b>Председатель СНО твоего факультета</b> – в разделе «Контакты» группы ВК
        """,
        'Дворец культуры ЧГУ': """
            Это не просто современная и круто оснащенная площадка, на которой проводятся концерты, спектакли, форумы, мастер-классы. Это Центр молодежной культуры Чувашии. На этой сцене, кстати, пела и танцевала Ольга Бузова. На этой же сцене можешь блистать и ты. По вопросам участия в творческой жизни университета обращайся к культоргу своего факультета.
            Дворец Культуры находится по адресу ул. Университетская, д. 38.
            <b>Группа ВК</b> – https://vk.com/dkchgu
            <b>Директор ДК ЧГУ</b> – Заворзаева Анна Васильевна
            <b>Культорг твоего факультета</b> – https://vk.com/@dkchgu-kultorgi-dk-chgu
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
            Это место, где можно реализовать свой творческий потенциал. Тебя ждет множество направлений, в которых работают опытные педагоги-наставники. 
            Отбор в студии будет проходить в начале учебного года. 
            Раскрывай свои таланты вместе с университетом.
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

    PHOTOS = {
        'Бизнес-инкубатор': 'businass_incub.jpg',
        'Автошкола': 'auto_school.jpg',
    }

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

    PHOTOS = {
        'Научная библиотека': 'slib.jpg',
        'Коворкинг': 'co-work.jpg',
        'Клуб настольных игр': 'board_games_club.jpg',
    }

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
    FIRST_GREETING = """
        Привет! Этот бот-помощник поможет тебе познакомиться с нашим университетом и его возможностями. 
        Расскажем все самое важное и как скрасить свою рутину внеучебной деятельностью.
        Пс, полезно будет, даже если ты не первак.
    """

    GREETING = """
        Что на этот раз?)
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
    def execute(cls, message, join=False):
        user, created = BotProfile2.objects.get_or_create(
            dict(
                user_guid=message['chat']['id'],
                current=cls.__name__,
            ),
            user_guid=message['chat']['id']
        )
        if created:
            return cls.send(message, cls.FIRST_GREETING)
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
