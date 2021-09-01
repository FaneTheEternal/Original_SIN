import re
import sys

from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from vk_api.exceptions import ApiError

from ..models import VkUser, IncomingProfile


def make_keyboard(cls, keyboard=None, one_time=True):
    if keyboard is None:
        keyboard = VkKeyboard(one_time=one_time)

    NEW_LINE = [i for i in range(len(cls.WORDS)) if i % 2 == 1]
    for i in range(len(cls.WORDS)):
        keyboard.add_button(
            cls.WORDS[i],
            color=VkKeyboardColor.SECONDARY
        )
        if i in NEW_LINE:
            keyboard.add_line()

    keyboard.add_button(
        cls.BACK,
        color=VkKeyboardColor.NEGATIVE
    )

    return keyboard


def send(vk, peer_id, message, keyboard, attachment):
    # cleanse message
    message = re.sub(' +', ' ', message)

    vk.messages.send(
        peer_id=peer_id,
        message=message,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
        attachment=attachment
    )


class Incoming(object):
    WORDS = [
        'Способы подачи документов',
        'Необходимые документы',
        'Сроки приема',
        'Вступительные испытания',
        'Бюджетные места',
        'Индивидуальные достижения',
        'Рейтинг поступающих',
        'Минимальные баллы',
        'Проходные баллы',
        'Платное обучение',
        'Калькулятор ЕГЭ',
    ]

    TEXT_ONLY = [
        'Способы подачи документов',
        'Необходимые документы',
        'Вступительные испытания',
        'Бюджетные места',
        'Индивидуальные достижения',
        'Рейтинг поступающих',
        'Минимальные баллы',
        'Проходные баллы',
        'Калькулятор ЕГЭ',
        'Платное обучение',
    ]

    ATTACHMENTS = {
        'Вступительные испытания': ['doc-88277426_605900611'],
        'Бюджетные места': ['doc-88277426_605900588'],
        'Индивидуальные достижения': ['doc-88277426_605900627'],
        'Проходные баллы': ['doc-88277426_605900642'],
        'Платное обучение': ['doc-88277426_605900658'],
    }

    BACK = 'Вернуться в основное меню'

    ADMISSION = 'Сроки приема'

    @classmethod
    def execute(cls, vk, user, text):
        profile, created = IncomingProfile.objects.get_or_create(
            user=user
        )
        message = ''
        attachment = None
        keyboard = None

        admission = Admission()

        if profile.status == IncomingProfile.ADMISSION:
            return admission.execute(vk, user, text)

        elif text == cls.ADMISSION:
            profile.status = IncomingProfile.ADMISSION
            profile.save()
            message = cls.TEXTS.get(text, '-')
            keyboard = admission.keyboard()

        elif text in cls.TEXT_ONLY:
            message = cls.TEXTS.get(text, '-')
            attachment = cls.ATTACHMENTS.get(text, None)
            keyboard = cls.keyboard()

        elif text == cls.BACK:
            from ..chat_bot import go_home
            profile.set_default(full=True)
            return go_home(vk, user)

        else:
            from ..chat_bot import sleep
            profile.set_default(full=True)
            return sleep(vk, user)

        try:
            send(vk, str(user.user_id), message, keyboard, attachment)
        except ApiError as pezdos:
            print('User_id: ', user.user_id, file=sys.stderr)
            print('Message: ', message, file=sys.stderr)
            print('Attachment: ', attachment, file=sys.stderr)
            print('Pezdos: ', pezdos, file=sys.stderr)

    @classmethod
    def keyboard(cls, keyboard=None, one_time=True):
        return make_keyboard(cls, keyboard, one_time)

    TEXTS = {
        'Способы подачи документов':
            """
    &#9993;  Прием документов осуществляется:
    1. Очно, в приемной комиссии университета по адресу: г. Чебоксары, ул. Университетская, 38
    2. В электронном виде, через Личный кабинет на сайте приемной комиссии https://priem.chuvsu.ru/
    3. Через портал Госуслуги  https://www.gosuslugi.ru/ 
    4. В бумажном виде через операторов почтовой связи общего пользования на адрес: 428015, Чувашская Республика, г. Чебоксары, Московский проспект, 15, Приемная комиссия.
    &#10071; Напоминаем, что абитуриент может подать документы в 5 вузов. В ЧувГУ можно выбрать до 10 направлений подготовки, специальностей.
    Режим работы приемной комиссии:  с 18 июня по 17 августа: пн – пт с 9:00 до 18:00, сб с 9:00 до 14:00, 
    с 18 по 31 августа: пн – пт с 9:00 до 17:00, сб с 9:00 до 14:00, вс – выходной. 
        """,

        'Необходимые документы':
            """
    1. Паспорт (стр. 2-3 + стр. с регистрацией).
    2. Документ об образовании (Аттестат или Диплом с приложением).
    3. СНИЛС (при наличии)
    4. Документы, подтверждающие индивидуальные достижения (при наличии).
    5. Документы, подтверждающие право на поступление в пределах особой квоты (при наличии).
    6. Документы, подтверждающие право на поступление в пределах целевой квоты (при наличии).
    7. Документы, подтверждающие право на поступление без испытаний (при наличии).
    8. Медицинская справка 086/у – необходима только при поступлении на «Лечебное дело», «Стоматология», «Педиатрия», «Фармация», «Психолого-педагогическое образование», «Электроэнергетика и электротехника», «Теплоэнергетика и теплотехника», «Наземные транспортно-технологические комплексы».
    Документы подаются лично в виде ксерокопий (с предъявлением оригинала), либо загружаются в виде скана/фото в форматеipg, pdf  размером не более 5 Мб.
    &#10071;  Оригинал документа об образовании (аттестата, диплома) может быть предоставлен в университет в течение первого года обучения.
        """,

        'Сроки приема':
            """
    Сроки начала и завершения приема документов, проведения вступительных испытаний и зачисления зависят от интересующего вас уровня образования. Выберите нужный уровень.
            """,

        'Вступительные испытания':
            """
    &#128313;  Бакалавриат, специалитет – прием по результатам ЕГЭ 2017-2021 гг. (для выпускников школ) или по результатам внутренних вступительных испытаний в вузе (для выпускников ссузов, вузов). 
    На направлениях «Дизайн», «Журналистика» и всех направлениях факультета искусств предусмотрены дополнительные внутренние испытания творческой (профессиональной) направленности. Полный перечень на сайте приемной комиссии vk.cc/axe8nQ и в прилагаемом документе.
    &#128313;  Магистратура – прием по результатам междисциплинарного экзамена по выбранному профилю. Программы экзаменов по ссылке vk.cc/axkD7e 
    &#128313;  Ординатура – прием по результатам тестирования. 
    &#128313;  Аспирантура – прием по результатам экзамена по специальной дисциплине.
            """,

        'Бюджетные места':
            """
    В 2021 году в ЧувГУ всего выделено 1727 бюджетных мест.  Из них:
    &#128313;  бакалавриат, специалитет – 1476 мест,
    &#128313;  магистратура – 137 мест,
    &#128313;  ординатура – 78 мест,
    &#128313;  аспирантура –  36 мест.
    Распределение бюджетных мест по направлениям, специальностям в прикрепленном документе &#128071;
            """,

        'Индивидуальные достижения':
            """
    Максимальная сумма баллов за результаты индивидуальных достижений – 10 баллов. Перечень индивидуальных достижений определен вузом, в него входят: академические успехи, спортивные достижения, волонтерская деятельность и др. Полный перечень учитываемых индивидуальных достижений в прикрепленном документе  &#128071;
            """,

        'Рейтинг поступающих':
            """
    &#128221;  На основании поданных абитуриентами документов формируется список поступающих (рейтинг). Список формируется отдельно на каждое направление, специальность с учетом формы обучения (очная, очно-заочная, заочная). Обновление происходит в режиме онлайн.
    &#11015; Поступающие располагаются в порядке убывания баллов - от высшего до самого маленького. Вместо ФИО поступающего указывается его ID (Личный код).
    При этом поступающие сгруппированы по категориям: 
    - без испытаний,
    - особые права,
    - целевой прием,
    - на общих основаниях,
    - по контракту.
    &#10071; Напоминаем, что в конкурсе на бюджетные места участвуют только те абитуриенты, которые в оформили заявление о согласии на зачисление в установленные сроки.
    Ссылка на рейтинг vk.cc/c3Lmex 
        """,

        'Минимальные баллы':
            """
    Минимальные баллы – это пороговые значения вступительных испытаний, позволяющие претендовать на поступление в вуз. С результатами ниже минимальных баллов поступающий не может быть принят в вуз, даже на платное обучение. 
    &#128311;  Бакалавриат, специалитет:
    Русский язык, География, История, Биология, Химия, Литература – 40 баллов
    Обществознание, Информатика – 45 баллов
    Математика, Физика – 39 баллов
    Иностранный язык – 30 баллов
    Русский язык, Биология, Химия, Физика (на специальности «Лечебное дело», «Педиатрия», «Стоматология», «Фармация») – 45 баллов
    Рисунок, Живопись, Сочинение, Теория музыки, Музыкальная специальность – 50 баллов
    &#128310;  Магистратура, ординатура, аспирантура:
    Междисциплинарный экзамен, тестирование, экзамен по специальности – 50 баллов
            """,

        'Проходные баллы':
            """
    Проходные баллы представляют собой итоги прошлогоднего приема на бюджет, они не являются гарантией зачисления в текущем году. Проходной балл определяется отдельно по каждому направлению подготовки, специальности.
    Проходные баллы 2020 года в прикрепленном документе &#128071;

            """,

        'Калькулятор ЕГЭ':
            """
    Специально для абитуриентов в ЧувГУ создан онлайн-сервис «Калькулятор ЕГЭ». Введите свои реальные или предполагаемые баллы ЕГЭ по предметам и сервис подберет подходящие направления, специальности. По каждому приводится описание, проходные баллы и бюджетные места за несколько лет, что поможет оценить шансы на поступление и принять верное решение.
    Ссылка на ресурс http://optimus.chuvsu.ru/services/ege-calculator/     
            """,

        'Платное обучение':
            """
    &#128196; Основанием для платного обучения является Договор об образовании. Заказчиком, оплачивающим обучение, может быть сам обучающийся (в случае достижения совершеннолетия) или его законный представитель (родитель или доверенное лицо). Для зачисления необходимо произвести оплату в размере не менее 10% от годовой стоимости обучения. 
    &#10071; Исходя из среднего балла результатов ЕГЭ или внутренних экзаменов (без учета индивидуальных достижений) предоставляется скидка:
    60-70 баллов – 7% 
    71-80 баллов – 10% 
    81 балл и выше – 20%
     
    Контакты Отдела по работе со студентами, обучающимися на договорной основе: 
    тел. +7 (8352) 58-11-46, 45-26-91 (доб. 2067), e-mail: market120@chuvsu.ru
    
    Стоимость обучения по очной, очно-заочной и заочной формам обучения в прикрепленном документе &#128071;
        """,
    }


class Admission(object):
    WORDS = [
        'Бакалавриат, специалитет',
        'Магистратура',
    ]

    BACK = 'Вернуться в основное меню'

    @classmethod
    def execute(cls, vk, user, text):
        profile, created = IncomingProfile.objects.get_or_create(
            user=user
        )
        attachment = None

        if text in cls.WORDS:
            message = cls.TEXTS.get(text, '-')
            profile.set_default()
            keyboard = Incoming.keyboard()

        elif text == cls.BACK:
            from ..chat_bot import go_home
            profile.set_default()
            return go_home(vk, user)

        else:
            from ..chat_bot import sleep
            return sleep(vk, user)

        try:
            send(vk, str(user.user_id), message, keyboard, attachment)
        except ApiError as pezdos:
            print('User_id: ', user.user_id, file=sys.stderr)
            print('Message: ', message, file=sys.stderr)
            print('Attachment: ', attachment, file=sys.stderr)
            print('Pezdos: ', pezdos, file=sys.stderr)

    @classmethod
    def keyboard(cls, keyboard=None, one_time=True):
        return make_keyboard(cls, keyboard, one_time)

    TEXTS = {
        'Бакалавриат, специалитет':
            """
    &#128309; ОЧНАЯ И ОЧНО-ЗАОЧНАЯ ФОРМА:
    18 июня – начало приема документов.
    &#10071; 19 июля – завершение приема документов от поступающих по результатам внутренних вступительных испытаний (на бюджет и платно).
    20-29 июля – проведение внутренних вступительных испытаний.
    &#10071; 29 июля – завершение приема документов от поступающих по результатам ЕГЭ.
    2 августа – размещение рейтинга (списка поступающих) на сайте.
    &#128310; Приоритетное зачисление (без вступительных испытаний, в пределах особой квоты, целевой квоты):
    4 августа – завершение приема заявлений о согласии на зачисление.
    6 августа – издание приказа о зачислении.
    &#128310; Зачисление по общему конкурсу:
    11 августа – завершается прием заявлений о согласии на зачисление,
    17 августа – издание приказа о зачислении.
    30 сентября – завершение приема документов от поступающих на платное обучение по результатам ЕГЭ.
    &#128309; ЗАОЧНАЯ ФОРМА:
    18 июня – начало приема документов.
    27 августа – завершение приема документов на бюджетные места.
    25 декабря – завершение приема документов на платное обучение. 

            """,
        'Магистратура':
            """
    18 июня – начало приема документов.
    09 августа – завершение приема документов на бюджетные места.
    10-12 августа – вступительные испытания (междисциплинарный экзамен).
    14 августа – размещение рейтинга (списка поступающих) на сайте.
    17 августа – завершение приема заявлений о согласии на зачисление.
    18 августа – издание приказа о зачислении.
    30 сентября – завершение приема документов на платное обучение по очной и очно-заочной форме.
    28-29 августа – вступительные испытания на платное обучение.
    25 декабря – завершение приема документов на платное обучение по заочной форме.
            """,
    }
