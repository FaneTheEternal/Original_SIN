import json

from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from ..models import QuestProfile


__all__ = ('QuestRoute')


ALLOW_QUEST = [
    'ReadyForTheStudentBodyQuest',
    'ProblemSolvingStyleQuest',
    'SelfMonitoringScaleQuest',
    'PsychologicalDefenseStrategyQuest',
    'AcceptanceScaleofOthersQuest',
]

FUKK_GO_BACK = 'Вернуться в основное меню'


def get_data(profile, created=False):
    if created or not profile.data:
        data = {
            'quest': None,
            'step': None,
            'points': None,
        }
        profile.data = json.dumps(data)
        profile.save()
        return data
    else:
        return json.loads(profile.data)


class QuestRoute(object):
    routs = {}

    @classmethod
    def load(cls):
        for quest in ALLOW_QUEST:
            quest_class = globals()[quest]
            cls.routs[quest_class.title] = quest_class

    @classmethod
    def execute(cls, vk, user, text):
        profile, created = QuestProfile.objects.get_or_create(
            user=user
        )

        cls.load()
        data = get_data(profile, created)
        quest = data.get('quest', None)

        if text == FUKK_GO_BACK:
            from ..chat_bot import fukk_go_back
            return fukk_go_back(vk, profile.user)

        elif quest:
            quest_class = globals()[quest]
            return quest_class.execute(vk, profile, text)

        elif text in list(cls.routs.keys()) + [FUKK_GO_BACK]:
            return cls.routs[text].execute(vk, profile, text)

        else:
            keyboard = cls.main_keyboard()
            vk.messages.send(
                peer_id=str(user.user_id),
                message='Хочешь узнать о себе больше? Мы приготовили для тебя несколько тестов. Выбирай!',
                random_id=get_random_id(),
                keyboard=keyboard.get_keyboard(),
            )

    @classmethod
    def main_keyboard(cls):
        keyboard = VkKeyboard(one_time=True)
        for quest, qclass in cls.routs.items():
            keyboard.add_button(label=quest, color=qclass.color)
            keyboard.add_line()
        keyboard.add_button(
            label=FUKK_GO_BACK,
            color=VkKeyboardColor.NEGATIVE
        )
        return keyboard


class QuestBase(object):
    columns = []
    steps = []
    title = None
    greetings = None
    attachment = None
    color = VkKeyboardColor.PRIMARY
    IGNORE = ['question', 'attachment']

    """
    step = {
        'question': str,
        'attachment': str|list|None,
        answer: {
            'column': str,
            'points': int
        }
    }
    """

    @classmethod
    def execute(cls, vk, profile, text):
        data = get_data(profile)
        step_num = data['step']
        if step_num is None:
            return cls.start(vk, profile)
        step = cls.steps[step_num]
        answer = step.get(text, None)
        if answer is None:
            return cls._send_question(vk, profile.user.user_id, step_num)

        column = answer['column']
        data[column] += answer['points']

        step_num += 1
        if step_num == len(cls.steps):
            return cls.end(vk, profile)

        data['step'] = step_num
        profile.data = json.dumps(data)
        profile.save()
        return cls._send_question(vk, profile.user.user_id, step_num)

    @staticmethod
    def send(vk, user_id, message: str, attachment=None, keyboard=None):
        message = message.replace('    ', '')
        vk.messages.send(
            peer_id=str(user_id),
            message=message,
            attachment=attachment,
            random_id=get_random_id(),
            keyboard=keyboard.get_keyboard() if keyboard else None,
        )

    @classmethod
    def _send_question(cls, vk, user_id, step_num):
        step = cls.steps[step_num]
        keyboard = VkKeyboard(one_time=True)
        for answer in step.keys():
            if answer in cls.IGNORE:
                continue
            keyboard.add_button(label=" ".join(answer.split()))
            keyboard.add_line()
        keyboard.add_button(
            label=FUKK_GO_BACK,
            color=VkKeyboardColor.NEGATIVE
        )

        attachment = step.get('attachment', None)

        cls.send(
            vk=vk,
            user_id=user_id,
            message=step['question'],
            attachment=attachment,
            keyboard=keyboard
        )

    @classmethod
    def start(cls, vk, profile):
        data = {
            'quest': cls.__name__,
            'step': 0,
        }
        data.update({
            i: 0 for i in cls.columns
        })
        profile.data = json.dumps(data)
        profile.save()
        cls.send(
            vk=vk,
            user_id=profile.user.user_id,
            message=cls.greetings,
            attachment=cls.attachment
        )
        return cls._send_question(vk, profile.user.user_id, 0)

    @classmethod
    def end(cls, vk, profile):
        raise NotImplementedError()

    @classmethod
    def send_end(cls, vk, profile, message, attachment=None):
        keyboard = QuestRoute.main_keyboard()
        user = profile.user
        profile.delete()
        return cls.send(
            vk=vk,
            user_id=user.user_id,
            message=message,
            attachment=attachment,
            keyboard=keyboard
        )


# Стиль решения проблем
class ProblemSolvingStyleQuest(QuestBase):
    title = 'Стиль решения проблем'
    greetings = """Каждый из нас в реальной жизни сталкивается с множеством проблем. При этом различают несколько стратегий их решения. Прочитайте внимательно каждое из 20 утверждений и выберите свой вариант ответа."""
    columns = [
        'Thinking',
        'Feeling',
        'Intuitive',
        'Sensitive'
    ]
    steps = [
        # 1
        {
            'question': '1.	Большинство людей считает, что я человек, стремящийся к объективности и логике.',
            'Абсолютно не согласен': {
                'column': 'Thinking',
                'points': 1
            },
            'Не согласен': {
                'column': 'Thinking',
                'points': 2
            },
            'Не уверен': {
                'column': 'Thinking',
                'points': 3
            },
            'Согласен': {
                'column': 'Thinking',
                'points': 4
            },
            'Абсолютно согласен': {
                'column': 'Thinking',
                'points': 5
            },
        },
        # 2
        {
            'question': '2.	Большинство людей сказало бы, что я эмоционален и способен мотивировать других.',
            'Абсолютно не согласен': {
                'column': 'Feeling',
                'points': 1
            },
            'Не согласен': {
                'column': 'Feeling',
                'points': 2
            },
            'Не уверен': {
                'column': 'Feeling',
                'points': 3
            },
            'Согласен': {
                'column': 'Feeling',
                'points': 4
            },
            'Абсолютно согласен': {
                'column': 'Feeling',
                'points': 5
            },
        },
        # 3
        {
            'question': '3.	Большинство людей уверено, что я детально разбираюсь в своей работе и аккуратно выполняю её.',
            'Абсолютно не согласен': {
                'column': 'Intuitive',
                'points': 1
            },
            'Не согласен': {
                'column': 'Intuitive',
                'points': 2
            },
            'Не уверен': {
                'column': 'Intuitive',
                'points': 3
            },
            'Согласен': {
                'column': 'Intuitive',
                'points': 4
            },
            'Абсолютно согласен': {
                'column': 'Intuitive',
                'points': 5
            },
        },
        # 4
        {
            'question': '4.	Большинство людей согласится, что я умный и сложный человек.',
            'Абсолютно не согласен': {
                'column': 'Sensitive',
                'points': 1
            },
            'Не согласен': {
                'column': 'Sensitive',
                'points': 2
            },
            'Не уверен': {
                'column': 'Sensitive',
                'points': 3
            },
            'Согласен': {
                'column': 'Sensitive',
                'points': 4
            },
            'Абсолютно согласен': {
                'column': 'Sensitive',
                'points': 5
            },
        },
        # 5
        {
            'question': '5.	Когда я сталкиваюсь с проблемой, я пытаюсь анализировать все факты и систематизировать их определённым образом.',
            'Абсолютно не согласен': {
                'column': 'Thinking',
                'points': 1
            },
            'Не согласен': {
                'column': 'Thinking',
                'points': 2
            },
            'Не уверен': {
                'column': 'Thinking',
                'points': 3
            },
            'Согласен': {
                'column': 'Thinking',
                'points': 4
            },
            'Абсолютно согласен': {
                'column': 'Thinking',
                'points': 5
            },
        },
        # 6
        {
            'question': '6.	Мне нравится доставлять удовольствие другим людям и по случаю принимать похвалу.',
            'Абсолютно не согласен': {
                'column': 'Feeling',
                'points': 1
            },
            'Не согласен': {
                'column': 'Feeling',
                'points': 2
            },
            'Не уверен': {
                'column': 'Feeling',
                'points': 3
            },
            'Согласен': {
                'column': 'Feeling',
                'points': 4
            },
            'Абсолютно согласен': {
                'column': 'Feeling',
                'points': 5
            },
        },
        # 7
        {
            'question': '7.	Я больше интересуюсь вопросами широкого профиля, а дела, отягощённые незначительными сиюминутными деталями, заставляют меня скучать.',
            'Абсолютно не согласен': {
                'column': 'Intuitive',
                'points': 1
            },
            'Не согласен': {
                'column': 'Intuitive',
                'points': 2
            },
            'Не уверен': {
                'column': 'Intuitive',
                'points': 3
            },
            'Согласен': {
                'column': 'Intuitive',
                'points': 4
            },
            'Абсолютно согласен': {
                'column': 'Intuitive',
                'points': 5
            },
        },
        # 8
        {
            'question': '8.	Обычно я сосредотачиваюсь на актуальных, требующих немедленного решения проблемах и предоставляю другим задумываться о далёком будущем.',
            'Абсолютно не согласен': {
                'column': 'Sensitive',
                'points': 1
            },
            'Не согласен': {
                'column': 'Sensitive',
                'points': 2
            },
            'Не уверен': {
                'column': 'Sensitive',
                'points': 3
            },
            'Согласен': {
                'column': 'Sensitive',
                'points': 4
            },
            'Абсолютно согласен': {
                'column': 'Sensitive',
                'points': 5
            },
        },
        # 9
        {
            'question': '9.	Когда мне нужно делать свою работу, я делаю её, несмотря на то, что в результате могут быть задеты чувства других людей.',
            'Абсолютно не согласен': {
                'column': 'Thinking',
                'points': 1
            },
            'Не согласен': {
                'column': 'Thinking',
                'points': 2
            },
            'Не уверен': {
                'column': 'Thinking',
                'points': 3
            },
            'Согласен': {
                'column': 'Thinking',
                'points': 4
            },
            'Абсолютно согласен': {
                'column': 'Thinking',
                'points': 5
            },
        },
        # 10
        {
            'question': '10.	Я больше ориентируюсь на людей, а не на выполнение задач.',
            'Абсолютно не согласен': {
                'column': 'Feeling',
                'points': 1
            },
            'Не согласен': {
                'column': 'Feeling',
                'points': 2
            },
            'Не уверен': {
                'column': 'Feeling',
                'points': 3
            },
            'Согласен': {
                'column': 'Feeling',
                'points': 4
            },
            'Абсолютно согласен': {
                'column': 'Feeling',
                'points': 5
            },
        },
        # 11
        {
            'question': '11.	Обычно я быстро решаю проблемы, не сосредоточиваясь на деталях.',
            'Абсолютно не согласен': {
                'column': 'Intuitive',
                'points': 1
            },
            'Не согласен': {
                'column': 'Intuitive',
                'points': 2
            },
            'Не уверен': {
                'column': 'Intuitive',
                'points': 3
            },
            'Согласен': {
                'column': 'Intuitive',
                'points': 4
            },
            'Абсолютно согласен': {
                'column': 'Intuitive',
                'points': 5
            },
        },
        # 12
        {
            'question': '12.	Перед тем, как вкладываться в какой-то проект, мне необходимо понять, что в нём является важным для меня лично.',
            'Абсолютно не согласен': {
                'column': 'Sensitive',
                'points': 1
            },
            'Не согласен': {
                'column': 'Sensitive',
                'points': 2
            },
            'Не уверен': {
                'column': 'Sensitive',
                'points': 3
            },
            'Согласен': {
                'column': 'Sensitive',
                'points': 4
            },
            'Абсолютно согласен': {
                'column': 'Sensitive',
                'points': 5
            },
        },
        # 13
        {
            'question': '13.	Я не даю проблемам выбить себя из колеи, насколько бы сложны они ни были.',
            'Абсолютно не согласен': {
                'column': 'Thinking',
                'points': 1
            },
            'Не согласен': {
                'column': 'Thinking',
                'points': 2
            },
            'Не уверен': {
                'column': 'Thinking',
                'points': 3
            },
            'Согласен': {
                'column': 'Thinking',
                'points': 4
            },
            'Абсолютно согласен': {
                'column': 'Thinking',
                'points': 5
            },
        },
        # 14
        {
            'question': '14.	Я способен хорошо понимать, как другие люди воспринимают проблемы и поставленные задачи.',
            'Абсолютно не согласен': {
                'column': 'Feeling',
                'points': 1
            },
            'Не согласен': {
                'column': 'Feeling',
                'points': 2
            },
            'Не уверен': {
                'column': 'Feeling',
                'points': 3
            },
            'Согласен': {
                'column': 'Feeling',
                'points': 4
            },
            'Абсолютно согласен': {
                'column': 'Feeling',
                'points': 5
            },
        },
        # 15
        {
            'question': '15.	Меня угнетает рутина, и я предпочитаю работать с новыми, сложными задачами.',
            'Абсолютно не согласен': {
                'column': 'Intuitive',
                'points': 1
            },
            'Не согласен': {
                'column': 'Intuitive',
                'points': 2
            },
            'Не уверен': {
                'column': 'Intuitive',
                'points': 3
            },
            'Согласен': {
                'column': 'Intuitive',
                'points': 4
            },
            'Абсолютно согласен': {
                'column': 'Intuitive',
                'points': 5
            },
        },
        # 16
        {
            'question': '16.	Мне нравится заниматься тем, что я хорошо умею, а столкновение с чем-то новым беспокоит меня.',
            'Абсолютно не согласен': {
                'column': 'Sensitive',
                'points': 1
            },
            'Не согласен': {
                'column': 'Sensitive',
                'points': 2
            },
            'Не уверен': {
                'column': 'Sensitive',
                'points': 3
            },
            'Согласен': {
                'column': 'Sensitive',
                'points': 4
            },
            'Абсолютно согласен': {
                'column': 'Sensitive',
                'points': 5
            },
        },
        # 17
        {
            'question': '17.	Мне не доставляет особого труда принимать жёсткие решения, когда это необходимо.',
            'Абсолютно не согласен': {
                'column': 'Thinking',
                'points': 1
            },
            'Не согласен': {
                'column': 'Thinking',
                'points': 2
            },
            'Не уверен': {
                'column': 'Thinking',
                'points': 3
            },
            'Согласен': {
                'column': 'Thinking',
                'points': 4
            },
            'Абсолютно согласен': {
                'column': 'Thinking',
                'points': 5
            },
        },
        # 18
        {
            'question': '18.	При работе в группе я предпочитаю атмосферу гармонии – даже в ущерб эффективности.',
            'Абсолютно не согласен': {
                'column': 'Feeling',
                'points': 1
            },
            'Не согласен': {
                'column': 'Feeling',
                'points': 2
            },
            'Не уверен': {
                'column': 'Feeling',
                'points': 3
            },
            'Согласен': {
                'column': 'Feeling',
                'points': 4
            },
            'Абсолютно согласен': {
                'column': 'Feeling',
                'points': 5
            },
        },
        # 19
        {
            'question': '19.	Мне по-настоящему нравится решать новые задачи.',
            'Абсолютно не согласен': {
                'column': 'Intuitive',
                'points': 1
            },
            'Не согласен': {
                'column': 'Intuitive',
                'points': 2
            },
            'Не уверен': {
                'column': 'Intuitive',
                'points': 3
            },
            'Согласен': {
                'column': 'Intuitive',
                'points': 4
            },
            'Абсолютно согласен': {
                'column': 'Intuitive',
                'points': 5
            },
        },
        # 20
        {
            'question': '20.	Я быстро учусь, но мне не нравятся отвлечённые прожектёрские концепции.',
            'Абсолютно не согласен': {
                'column': 'Sensitive',
                'points': 1
            },
            'Не согласен': {
                'column': 'Sensitive',
                'points': 2
            },
            'Не уверен': {
                'column': 'Sensitive',
                'points': 3
            },
            'Согласен': {
                'column': 'Sensitive',
                'points': 4
            },
            'Абсолютно согласен': {
                'column': 'Sensitive',
                'points': 5
            },
        },
    ]

    @classmethod
    def end(cls, vk, profile):
        data = get_data(profile)
        thinking = data.get('Thinking', 0)
        feeling = data.get('Feeling', 0)
        intuitive = data.get('Intuitive', 0)
        sensitive = data.get('Sensitive', 0)
        message = ''
        attachment = None
        top = max(thinking, feeling, intuitive, sensitive)
        if top == thinking:
            message = 'Вам присущ мыслительный тип решения проблем. Этому типу характерно следование собственным законам и попытка привести имеющиеся сведения о содержании проблемы в систему однозначных понятийных связей. Для мыслительного типа характерна рациональность в решении возникающих проблем, стремление путём размышления найти возможные варианты решения проблем на основании логики и объективного анализа сложившейся ситуации.'
            attachment = 'photo-88277426_457239033'
        elif top == feeling:
            message = 'Вам присущ чувствующий тип решения проблем. Для вас характерно принятие или отвержение вариантов решения проблемы на основании субъективных оценочных суждений: хорошо/плохо, красиво/некрасиво. Для чувствующего типа характерна рефлексия, попытка разобраться с тем, вызывает ли тот или иной вариант решения проблемы субъективное противоречие вне зависимости от того, насколько формально "правильным" оно представляется.'
            attachment = 'photo-88277426_457239025'
        elif top == intuitive:
            message = 'Вам присущ интуитивный тип решения проблем. Вы ориентируетесь на малоосознаваемые детали в целостном, готовом содержании проблемы, её внешних и внутренних признаков или их сочетаний. Для интуитивного типа характерна определённая иррациональность, когда принятие того или иного решения порой осуществляется с опорой на не вполне объяснимые и чётко определённые бессознательные представления о возникшей проблеме.'
            attachment = 'photo-88277426_457239026'
        elif top == sensitive:
            message = 'Вам присущ ощущающий тип решения проблем. Вы непосредственно и конкретно воспринимаете проблемы. Ощущающий тип при столкновении с проблемой склонен поступать субъективным образом, зависящим от специфического восприятия сложившейся ситуации, из-за чего может возникать определённая иррациональность, когда внешние проявления проблемы становятся важнее её внутреннего содержания.'
            attachment = 'photo-88277426_457239027'

        if thinking == feeling == intuitive == sensitive:
            message = 'Всего различают 4 типа решения проблем: мыслительный, чувствующий, интуитивный, ощущающий. Вы сочетаете в себе признаки всех четырех типов. Выбираемый Вами метод решения (рациональный или иррациональный, объективный или субъективный) зависит во многом от специфики возникшей проблемы.'
            attachment = 'photo-88277426_457239049'

        cls.send_end(vk, profile, message, attachment)


# Шкала самомониторнига
class SelfMonitoringScaleQuest(QuestBase):
    title = 'Шкала самомониторнига'
    greetings = """Каждый человек в той или иной степени осуществляет контроль над своим поведением и, тем самым, воздействует на впечатление, которое складывается о нём у окружающих. Эта способность называется коммуникативным контролем (самомониторингом).
        Вам будет предложено 18 высказываний. Если вы считаете, что утверждение подходит к описанию вашего поведения, выбирайте ответ «верно», если не подходит – «не верно»."""
    columns = ['Default', 'Sex']
    steps = [
        # 1
        {
            'question': '1.	Мне трудно подражать поведению других людей.',
            'Верно': {
                'column': 'Default',
                'points': 0
            },
            'Не верно': {
                'column': 'Default',
                'points': 1
            }
        },
        # 2
        {
            'question': '2.	На встречах, вечеринках, в компании я не пытаюсь сделать или сказать то, что должно нравиться другим людям.',
            'Верно': {
                'column': 'Default',
                'points': 0
            },
            'Не верно': {
                'column': 'Default',
                'points': 1
            }
        },
        # 3
        {
            'question': '3.	Я могу защитить только те идеи, в которые верю сам.',
            'Верно': {
                'column': 'Default',
                'points': 0
            },
            'Не верно': {
                'column': 'Default',
                'points': 1
            }
        },
        # 4
        {
            'question': '4.	Я могу импровизировать речь даже по такой теме, в которой я совсем не разбираюсь.',
            'Верно': {
                'column': 'Default',
                'points': 1
            },
            'Не верно': {
                'column': 'Default',
                'points': 0
            }
        },
        # 5
        {
            'question': '5. Я думаю, что у меня есть способность оказывать впечатление на других людей и развлекать их.',
            'Верно': {
                'column': 'Default',
                'points': 1
            },
            'Не верно': {
                'column': 'Default',
                'points': 0
            }
        },
        # 6
        {
            'question': '6. Я, вероятно, мог бы стать хорошим актёром.',
            'Верно': {
                'column': 'Default',
                'points': 1
            },
            'Не верно': {
                'column': 'Default',
                'points': 0
            }
        },
        # 7
        {
            'question': '7. В группе я редко являюсь центром внимания.',
            'Верно': {
                'column': 'Default',
                'points': 0
            },
            'Не верно': {
                'column': 'Default',
                'points': 1
            }
        },
        # 8
        {
            'question': '8. В различных ситуациях и с разными людьми я веду себя самым разнообразным образом.',
            'Верно': {
                'column': 'Default',
                'points': 1
            },
            'Не верно': {
                'column': 'Default',
                'points': 0
            }
        },
        # 9
        {
            'question': '9. Вряд ли я достигаю успеха тогда, когда пытаюсь понравиться другим людям.',
            'Верно': {
                'column': 'Default',
                'points': 0
            },
            'Не верно': {
                'column': 'Default',
                'points': 1
            }
        },
        # 10
        {
            'question': '10. Я не всегда тот человек, каким кажусь другим людям.',
            'Верно': {
                'column': 'Default',
                'points': 1
            },
            'Не верно': {
                'column': 'Default',
                'points': 0
            }
        },
        # 11
        {
            'question': '11. Я не изменю своего мнения или поведения, чтобы понравиться другим людям.',
            'Верно': {
                'column': 'Default',
                'points': 0
            },
            'Не верно': {
                'column': 'Default',
                'points': 1
            }
        },
        # 12
        {
            'question': '12. Я согласился бы быть тамадой на вечеринке.',
            'Верно': {
                'column': 'Default',
                'points': 1
            },
            'Не верно': {
                'column': 'Default',
                'points': 0
            }
        },
        # 13
        {
            'question': '13. Я никогда не был удачен в играх, требующих импровизации.',
            'Верно': {
                'column': 'Default',
                'points': 0
            },
            'Не верно': {
                'column': 'Default',
                'points': 1
            }
        },
        # 14
        {
            'question': '14. Мне трудно изменить своё поведение, чтобы соответствовать определённой ситуации или подстроиться под определённого человека.',
            'Верно': {
                'column': 'Default',
                'points': 0
            },
            'Не верно': {
                'column': 'Default',
                'points': 1
            }
        },
        # 15
        {
            'question': '15. На вечеринках и в компании я предоставляю другим людям возможность рассказывать шутки и анекдоты.',
            'Верно': {
                'column': 'Default',
                'points': 0
            },
            'Не верно': {
                'column': 'Default',
                'points': 1
            }
        },
        # 16
        {
            'question': '16. Я чувствую себя немного скованным в группах и компаниях, и не могу в полной мере выразить себя.',
            'Верно': {
                'column': 'Default',
                'points': 0
            },
            'Не верно': {
                'column': 'Default',
                'points': 1
            }
        },
        # 17
        {
            'question': '17. Я могу смотреть в глаза другому и невозмутимо лгать, если это надо для дела.',
            'Верно': {
                'column': 'Default',
                'points': 1
            },
            'Не верно': {
                'column': 'Default',
                'points': 0
            }
        },
        # 18
        {
            'question': '18. Я могу обмануть других людей тем, что кажусь дружелюбным по отношению к ним, когда в действительности они мне вовсе не симпатичны.',
            'Верно': {
                'column': 'Default',
                'points': 1
            },
            'Не верно': {
                'column': 'Default',
                'points': 0
            }
        },
        # Пол
        {
            'question': 'Укажите ваш пол',
            'М': {
                'column': 'Sex',
                'points': 1
            },
            'Ж': {
                'column': 'Sex',
                'points': 0
            }
        },
    ]

    @classmethod
    def end(cls, vk, profile):
        data = get_data(profile)
        score = data.get('Default', 0)
        sex = bool(data.get('Sex', 1))
        result = None
        if sex:
            if 0 <= score <= 6:
                result = 1
            elif 7 <= score <= 13:
                result = 2
            else:
                result = 3
        else:
            if 0 <= score <= 5:
                result = 1
            elif 6 <= score <= 13:
                result = 2
            else:
                result = 3

        message = ''
        attachment = None

        if result == 1:
            message = 'Вы относитесь к людям с низким коммуникативным контролем. Такие люди непосредственны и открыты, но могут восприниматься окружающими как излишне прямолинейные и навязчивые. Они мало озабочены адекватностью своего поведения и эмоциональной экспрессии и не обращают внимания на нюансы поведения других людей. Их поведение и эмоции зависят в большей степени от их внутреннего состояния, а не от требований ситуации.'
            attachment = 'photo-88277426_457239029'
        elif result == 2:
            message = 'Вы относитесь к людям со средним коммуникативным контролем. В общении вы непосредственны, искренне относитесь к другим людям. При этом сдержаны в эмоциональных проявлениях, соотносите свои реакции с поведением окружающих людей, доброжелательны.'
            attachment = 'photo-88277426_457239051'
        else:
            message = 'Вы относитесь к людям с высоким уровнем коммуникативного контроля. Такие люди постоянно следят за собой, хорошо осведомлены, где и как себя вести, управляют своими эмоциональными проявлениями. Их поведение сильно варьирует в зависимости от ситуации. Они эффективно контролируют свое поведение и без труда могут создать у окружающих нужное впечатление о себе. Вместе с тем, испытывают значительные трудности в спонтанности самовыражения, не любят непрогнозируемых ситуаций.'
            attachment = 'photo-88277426_457239028'

        cls.send_end(vk, profile, message, attachment)


# Стратегия психологической защиты
class PsychologicalDefenseStrategyQuest(QuestBase):
    title = 'Стратегия психологической защиты'
    greetings = """Знание особенностей коммуникативного поведения помогает избегать ненужных конфликтов в общении и действовать психологически грамотно. Различают несколько стратегий психологической защиты: миролюбие, избегание и агрессия. Тест позволит определить, какая из них является доминирующей для вас.
        Тест включает 24 вопроса, касающихся различных сторон жизни. На каждый вопрос предлагается три варианта ответа. Не тратьте время на раздумья, давайте первый естественный ответ, который приходит Вам в голову."""
    columns = ['Peacefulness', 'Avoidance', 'Aggression']
    steps = [
        # 1
        {
            'question': """1. Зная себя, вы можете сказать:
                A. я скорее человек миролюбивый, покладистый
                B. я скорее человек гибкий, способный обходить острые ситуации, избегать конфликтов
                C. я скорее человек, идущий напрямую, бескомпромиссный, категоричный""",
            'A': {
                'column': 'Peacefulness',
                'points': 1
            },
            'B': {
                'column': 'Avoidance',
                'points': 1
            },
            'C': {
                'column': 'Aggression',
                'points': 1
            }
        },
        # 2
        {
            'question': """2. Когда вы мысленно выясняете отношения со своим обидчиком, то чаще всего:
                A. ищете способ примирения
                B. обдумываете способ не иметь с ним дел
                C. размышляете о том, как его наказать или поставить на место""",
            'A': {
                'column': 'Peacefulness',
                'points': 1
            },
            'B': {
                'column': 'Avoidance',
                'points': 1
            },
            'C': {
                'column': 'Aggression',
                'points': 1
            }
        },
        # 3
        {
            'question': """3.	В спорной ситуации, когда человек явно не старается или не хочет вас понять, вы вероятнее всего:
                A. будете спокойно добиваться того, чтобы он вас понял
                B. постараетесь свернуть с ним общение
                C. будете горячиться, обижаться или злиться""",
            'A': {
                'column': 'Peacefulness',
                'points': 1
            },
            'B': {
                'column': 'Avoidance',
                'points': 1
            },
            'C': {
                'column': 'Aggression',
                'points': 1
            }
        },
        # 4
        {
            'question': """4. Если защищая свои важные интересы, вы почувствуете, что можете поссориться с хорошим человеком, то:
                A. пойдёте на значительные уступки
                B. отступите от своих притязаний
                C. будете отстаивать свои интересы""",
            'A': {
                'column': 'Peacefulness',
                'points': 1
            },
            'B': {
                'column': 'Avoidance',
                'points': 1
            },
            'C': {
                'column': 'Aggression',
                'points': 1
            }
        },
        # 5
        {
            'question': """5. В ситуации, где вас пытаются обидеть или унизить, вы скорее всего:
                A. постараетесь запастись терпением и довести дело до конца
                B. дипломатичным образом уйдете от контактов
                C. дадите достойный отпор""",
            'A': {
                'column': 'Peacefulness',
                'points': 1
            },
            'B': {
                'column': 'Avoidance',
                'points': 1
            },
            'C': {
                'column': 'Aggression',
                'points': 1
            }
        },
        # 6
        {
            'question': """6. Во взаимодействии с властным и в то же время несправедливым руководителем вы:
                A. сможете сотрудничать во имя интересов дела
                B. постараетесь как можно меньше контактировать с ними
                C. будете сопротивляться его стилю, активно защищая свои интересы""",
            'A': {
                'column': 'Peacefulness',
                'points': 1
            },
            'B': {
                'column': 'Avoidance',
                'points': 1
            },
            'C': {
                'column': 'Aggression',
                'points': 1
            }
        },
        # 7
        {
            'question': """7. Если решение вопроса зависит только от вас, кто-то задел ваше самолюбие, то вы:
                A. пойдёте ему навстречу
                B. уйдёте от конкретного решения
                C. решите вопрос не в пользу партнёра""",
            'A': {
                'column': 'Peacefulness',
                'points': 1
            },
            'B': {
                'column': 'Avoidance',
                'points': 1
            },
            'C': {
                'column': 'Aggression',
                'points': 1
            }
        },
        # 8
        {
            'question': """8. Если кто-то из друзей время от времени будет позволять себе обидные выпады в ваш адрес, вы:
                A. не станете придавать этому особого значения
                B. постараетесь ограничить или прекратить контакты
                C. всякий раз дадите достойный отпор""",
            'A': {
                'column': 'Peacefulness',
                'points': 1
            },
            'B': {
                'column': 'Avoidance',
                'points': 1
            },
            'C': {
                'column': 'Aggression',
                'points': 1
            }
        },
        # 9
        {
            'question': """9. Если у кого-то из окружающих есть претензии к вам, и он при этом раздражён, то вам привычнее:
                A. прежде успокоить его, а затем реагировать на претензии
                B. избежать выяснения отношений с партнёром и таком состоянии
                C. поставить его на своё место или прервать""",
            'A': {
                'column': 'Peacefulness',
                'points': 1
            },
            'B': {
                'column': 'Avoidance',
                'points': 1
            },
            'C': {
                'column': 'Aggression',
                'points': 1
            }
        },
        # 10
        {
            'question': """10.	Если кто-нибудь станет рассказывать вам о том плохом, что говорят о вас другие, то вы:
                A. тактично выслушаете все до конца
                B. пропустите мимо ушей
                C. прервёте рассказ на полуслове""",
            'A': {
                'column': 'Peacefulness',
                'points': 1
            },
            'B': {
                'column': 'Avoidance',
                'points': 1
            },
            'C': {
                'column': 'Aggression',
                'points': 1
            }
        },
        # 11
        {
            'question': """11.	Если кое-кто слишком проявляет напористость и хочет получить выгоду за ваш счёт, то вы:
                A. пойдёте на уступку ради мира
                B. уклонитесь от окончательного решения в расчёте на то, что партнёр успокоится и тогда вы вернётесь к вопросу
                C. однозначно дадите понять партнёру, что он не получит выгоду за ваш счёт""",
            'A': {
                'column': 'Peacefulness',
                'points': 1
            },
            'B': {
                'column': 'Avoidance',
                'points': 1
            },
            'C': {
                'column': 'Aggression',
                'points': 1
            }
        },
        # 12
        {
            'question': """12.	Когда вы имеете дело с кем-то, кто действует по принципу «урвать побольше», вы:
                A. терпеливо добиваетесь своих целей
                B. предпочитаете ограничить взаимодействие с ним
                C. решительно ставите такого партнёра на место""",
            'A': {
                'column': 'Peacefulness',
                'points': 1
            },
            'B': {
                'column': 'Avoidance',
                'points': 1
            },
            'C': {
                'column': 'Aggression',
                'points': 1
            }
        },
        # 13
        {
            'question': """13.	Имея дело с нагловатой личностью, вы:
                A. находите к ней подход посредством терпения и дипломатии
                B. сводите общение до минимума
                C. действуете теми же методами""",
            'A': {
                'column': 'Peacefulness',
                'points': 1
            },
            'B': {
                'column': 'Avoidance',
                'points': 1
            },
            'C': {
                'column': 'Aggression',
                'points': 1
            }
        },
        # 14
        {
            'question': """14.	Когда спорщик настроен к вам враждебно, вы обычно:
                A. спокойно и терпеливо преодолеваете его настрой
                B. уходите от общения
                C. осаждаете его или отвечаете тем же""",
            'A': {
                'column': 'Peacefulness',
                'points': 1
            },
            'B': {
                'column': 'Avoidance',
                'points': 1
            },
            'C': {
                'column': 'Aggression',
                'points': 1
            }
        },
        # 15
        {
            'question': """15.	Когда вам задают неприятные, «подковыривающие» вопросы, вы чаще всего:
                A. спокойно отвечаете на них
                B. уходите от прямых ответов
                C. «заводитесь», теряете самообладание""",
            'A': {
                'column': 'Peacefulness',
                'points': 1
            },
            'B': {
                'column': 'Avoidance',
                'points': 1
            },
            'C': {
                'column': 'Aggression',
                'points': 1
            }
        },
        # 16
        {
            'question': """16.	Когда возникают острые разногласия между вами и окружающим, то это чаще всего:
                A. заставляет вас искать выход из положения, находить компромисс, идти на уступки
                B. побуждает сглаживать противоречия, не подчёркивать различия в позициях
                C. активизирует желание доказать свою правоту""",
            'A': {
                'column': 'Peacefulness',
                'points': 1
            },
            'B': {
                'column': 'Avoidance',
                'points': 1
            },
            'C': {
                'column': 'Aggression',
                'points': 1
            }
        },
        # 17
        {
            'question': """17.	Если кто-то выигрывает в споре, вам привычнее:
                A. поздравить его с победой
                B. сделать вид, что ничего особенного не происходит
                C. «сражаться до последнего патрона»""",
            'A': {
                'column': 'Peacefulness',
                'points': 1
            },
            'B': {
                'column': 'Avoidance',
                'points': 1
            },
            'C': {
                'column': 'Aggression',
                'points': 1
            }
        },
        # 18
        {
            'question': """18.	В случаях, когда отношения с окружающими обретают конфликтный характер, вы взяли себе за правило:
                A. «мир любой ценой» — признать своё поражение, принести извинения, пойти на встречу пожеланиям партнёра
                B. «пас в сторону» — ограничить контакты, уйти от спора
                C. «расставить точки над «и» — выяснить все разногласия, непременно найти выход из ситуации""",
            'A': {
                'column': 'Peacefulness',
                'points': 1
            },
            'B': {
                'column': 'Avoidance',
                'points': 1
            },
            'C': {
                'column': 'Aggression',
                'points': 1
            }
        },
        # 19
        {
            'question': """19.	Когда конфликт касается ваших интересов, то вам чаще всего удаётся его выигрывать:
                A. благодаря дипломатии и гибкости ума
                B. за счёт выдержки и терпения
                C. за счёт темперамента и эмоций""",
            'A': {
                'column': 'Peacefulness',
                'points': 1
            },
            'B': {
                'column': 'Avoidance',
                'points': 1
            },
            'C': {
                'column': 'Aggression',
                'points': 1
            }
        },
        # 20
        {
            'question': """20.	Если кто-либо намеренно заденет ваше самолюбие, вы:
                A. мягко и корректно сделаете ему замечание
                B. не станете обострять ситуацию, сделаете вид, будто ничего не случилось
                C. дадите достойный отпор""",
            'A': {
                'column': 'Peacefulness',
                'points': 1
            },
            'B': {
                'column': 'Avoidance',
                'points': 1
            },
            'C': {
                'column': 'Aggression',
                'points': 1
            }
        },
        # 21
        {
            'question': """21.	Когда близкие критикуют вас, то вы:
                A. принимаете их замечания с благодарностью
                B. стараетесь не обращать на критику внимание
                C. раздражаетесь, сопротивляетесь или злитесь""",
            'A': {
                'column': 'Peacefulness',
                'points': 1
            },
            'B': {
                'column': 'Avoidance',
                'points': 1
            },
            'C': {
                'column': 'Aggression',
                'points': 1
            }
        },
        # 22
        {
            'question': """22.	Если кто-либо из родных или близких говорит вам неправду, вы обычно предпочитаете:
                A. спокойно и тактично добиваться истины
                B. сделать вид, что не замечаете ложь, обойти неприятный оборот дела
                C. решительно вывести лгуна на «чистую воду»""",
            'A': {
                'column': 'Peacefulness',
                'points': 1
            },
            'B': {
                'column': 'Avoidance',
                'points': 1
            },
            'C': {
                'column': 'Aggression',
                'points': 1
            }
        },
        # 23
        {
            'question': """23.	Когда вы раздражены, нервничаете, то чаще всего:
                A. ищите сочувствия, понимания
                B. уединяетесь, чтобы не проявить своё состояние на партнёрах
                C. на ком-нибудь отыгрываетесь, ищете «козла отпущения»""",
            'A': {
                'column': 'Peacefulness',
                'points': 1
            },
            'B': {
                'column': 'Avoidance',
                'points': 1
            },
            'C': {
                'column': 'Aggression',
                'points': 1
            }
        },
        # 24
        {
            'question': """24. Когда кто-то, менее достойный и способный, чем вы, получает поощрение начальства, вы:
                A. радуетесь за партнёра
                B. не придаёте особого значения факту
                C. расстраиваетесь, огорчаетесь или злитесь""",
            'A': {
                'column': 'Peacefulness',
                'points': 1
            },
            'B': {
                'column': 'Avoidance',
                'points': 1
            },
            'C': {
                'column': 'Aggression',
                'points': 1
            }
        },
    ]

    @classmethod
    def end(cls, vk, profile):
        data = get_data(profile)

        peacefulness = data.get('Peacefulness', 0)
        avoidance = data.get('Avoidance', 0)
        aggression = data.get('Aggression', 0)
        top = max(peacefulness, avoidance, aggression)

        message = ''
        attachment = None
        if top == peacefulness:
            message = 'Ваша доминирующая стратегия – «миролюбие». Миролюбие предполагает партнерство и сотрудничество, умение идти на компромиссы, делать уступки и быть податливым, готовность жертвовать некоторыми своими интересами во имя главного – сохранения достоинства. В ряде случаев миролюбие означает приспособление, стремление уступать напору собеседника, не обострять отношения и не ввязываться в конфликты, чтобы не подвергать испытаниям свое "Я". Для эффективного использования этой стратегии требуется определённый склад личности: подходящий характер (мягкий, уравновешенный, коммуникабельный) и высокий уровень интеллекта.'
            attachment = 'photo-88277426_457239030'
        elif top == avoidance:
            message = 'Ваша доминирующая стратегия – «избегание». Она основана на экономии интеллектуальных и эмоциональных ресурсов, попытке без боя покинуть зону конфликтов и напряжений. Иногда избегание обусловлено особенностями человека и предпочтительно в тех случаях, когда у него бедные эмоции, посредственный ум, вялый темперамент. В других случаях человек благодаря своему интеллекту способен вообще не связываться с теми, кто может ему досадить. Иногда человек умеет вовремя сдержаться, заставив себя обойти острые углы в общении и конфликтные ситуации. Избегание предъявляет повышенные требования к нервной системе и воле.'
            attachment = 'photo-88277426_457239031'
        else:
            message = 'Ваша доминирующая стратегия – «агрессия». В ее основе лежит поведение, приносящее физический ущерб людям или вызывающее у них психологический дискомфорт (отрицательные переживания, состояния напряженности, страха, подавленности). Агрессивное поведение может быть связано не только с защитой собственной личности и чувства самооценки, но и быть средством достижения какой-то значимой цели, способа психологической разрядки или способа получения удовлетворения. Агрессия в различных формах, жёстких и мягких, присутствует во многих ситуациях межличностного общения. Чем сильнее угроза для личности, тем сильнее проявляется ей агрессивность, которая с помощью интеллекта может обретать новый смысл и тем самым усиливаться.'
            attachment = 'photo-88277426_457239032'

        if peacefulness == avoidance == aggression:
            message = 'У вас нет ярко выраженной, доминирующей стратегии психологической защиты. В зависимости от ситуации вы можете вести себя миролюбиво либо избегать конфликтов, в редких случаях способны прибегать к агрессии.'
            attachment = 'photo-88277426_457239050'

        cls.send_end(vk, profile, message, attachment)


# Шкала оценки принятия других
class AcceptanceScaleofOthersQuest(QuestBase):
    title = 'Шкала оценки принятия других'
    greetings = """Эта шкала оценки дружественности-враждебности к окружающим людям, к миру в ходе общения. Встречаются два типа реагирования во время общения: реактивное и проактивное. Реактивное – отсутствие управления собой, даже если есть умение подавить вспышку эмоций. Проактивное - когда между стимулом и реакцией, существует пауза для осмысления и выбора наилучшей реакции. Проактивные люди обладают свободой выбора, как реагировать на то, либо иное событие.
        Вам будет предложено 18 утверждений, по каждому из них выберите вариант ответа, наиболее близкий Вам."""
    columns = ['Default']
    steps = [
        # 1
        {
            'question': '1.	Людей достаточно легко ввести в заблуждение.',
            'Всегда': {
                'column': 'Default',
                'points': 1
            },
            'Часто': {
                'column': 'Default',
                'points': 2
            },
            'Редко': {
                'column': 'Default',
                'points': 3
            },
            'Очень редко': {
                'column': 'Default',
                'points': 4
            },
            'Никогда': {
                'column': 'Default',
                'points': 5
            },
        },
        # 2
        {
            'question': '2.	Мне нравятся люди, с которыми я знаком(-а).',
            'Всегда': {
                'column': 'Default',
                'points': 5
            },
            'Часто': {
                'column': 'Default',
                'points': 4
            },
            'Редко': {
                'column': 'Default',
                'points': 3
            },
            'Очень редко': {
                'column': 'Default',
                'points': 2
            },
            'Никогда': {
                'column': 'Default',
                'points': 1
            },
        },
        # 3
        {
            'question': '3.	В наше время люди имеют очень низкие моральные принципы.',
            'Всегда': {
                'column': 'Default',
                'points': 1
            },
            'Часто': {
                'column': 'Default',
                'points': 2
            },
            'Редко': {
                'column': 'Default',
                'points': 3
            },
            'Очень редко': {
                'column': 'Default',
                'points': 4
            },
            'Никогда': {
                'column': 'Default',
                'points': 5
            },
        },
        # 4
        {
            'question': '4.	Большинство людей думают о себе только положительно, редко обращаясь к своим отрицательным качествам.',
            'Всегда': {
                'column': 'Default',
                'points': 1
            },
            'Часто': {
                'column': 'Default',
                'points': 2
            },
            'Редко': {
                'column': 'Default',
                'points': 3
            },
            'Очень редко': {
                'column': 'Default',
                'points': 4
            },
            'Никогда': {
                'column': 'Default',
                'points': 5
            },
        },
        # 5
        {
            'question': '5.	Я чувствую себя комфортно практически с любым человеком.',
            'Всегда': {
                'column': 'Default',
                'points': 5
            },
            'Часто': {
                'column': 'Default',
                'points': 4
            },
            'Редко': {
                'column': 'Default',
                'points': 3
            },
            'Очень редко': {
                'column': 'Default',
                'points': 2
            },
            'Никогда': {
                'column': 'Default',
                'points': 1
            },
        },
        # 6
        {
            'question': '6.	Всё, о чём люди говорят в наше время, сводится к разговорам о фильмах, телевидении и других глупых вещах подобного рода.',
            'Всегда': {
                'column': 'Default',
                'points': 1
            },
            'Часто': {
                'column': 'Default',
                'points': 2
            },
            'Редко': {
                'column': 'Default',
                'points': 3
            },
            'Очень редко': {
                'column': 'Default',
                'points': 4
            },
            'Никогда': {
                'column': 'Default',
                'points': 5
            },
        },
        # 7
        {
            'question': '7.	Если кто-либо начал делать одолжение другим людям, то они сразу же перестают уважать его.',
            'Всегда': {
                'column': 'Default',
                'points': 1
            },
            'Часто': {
                'column': 'Default',
                'points': 2
            },
            'Редко': {
                'column': 'Default',
                'points': 3
            },
            'Очень редко': {
                'column': 'Default',
                'points': 4
            },
            'Никогда': {
                'column': 'Default',
                'points': 5
            },
        },
        # 8
        {
            'question': '8.	Люди думают только о себе.',
            'Всегда': {
                'column': 'Default',
                'points': 1
            },
            'Часто': {
                'column': 'Default',
                'points': 2
            },
            'Редко': {
                'column': 'Default',
                'points': 3
            },
            'Очень редко': {
                'column': 'Default',
                'points': 4
            },
            'Никогда': {
                'column': 'Default',
                'points': 5
            },
        },
        # 9
        {
            'question': '9.	Люди всегда чем-то недовольны и ищут что-нибудь новое.',
            'Всегда': {
                'column': 'Default',
                'points': 1
            },
            'Часто': {
                'column': 'Default',
                'points': 2
            },
            'Редко': {
                'column': 'Default',
                'points': 3
            },
            'Очень редко': {
                'column': 'Default',
                'points': 4
            },
            'Никогда': {
                'column': 'Default',
                'points': 5
            },
        },
        # 10
        {
            'question': '10. Причуды большинства людей очень трудно вытерпеть.',
            'Всегда': {
                'column': 'Default',
                'points': 1
            },
            'Часто': {
                'column': 'Default',
                'points': 2
            },
            'Редко': {
                'column': 'Default',
                'points': 3
            },
            'Очень редко': {
                'column': 'Default',
                'points': 4
            },
            'Никогда': {
                'column': 'Default',
                'points': 5
            },
        },
        # 11
        {
            'question': '11. Людям определённо необходим сильный и умный лидер.',
            'Всегда': {
                'column': 'Default',
                'points': 1
            },
            'Часто': {
                'column': 'Default',
                'points': 2
            },
            'Редко': {
                'column': 'Default',
                'points': 3
            },
            'Очень редко': {
                'column': 'Default',
                'points': 4
            },
            'Никогда': {
                'column': 'Default',
                'points': 5
            },
        },
        # 12
        {
            'question': '12. Мне нравится быть в одиночестве, вдали от людей.',
            'Всегда': {
                'column': 'Default',
                'points': 1
            },
            'Часто': {
                'column': 'Default',
                'points': 2
            },
            'Редко': {
                'column': 'Default',
                'points': 3
            },
            'Очень редко': {
                'column': 'Default',
                'points': 4
            },
            'Никогда': {
                'column': 'Default',
                'points': 5
            },
        },
        # 13
        {
            'question': '13. Люди не всегда честно ведут себя с другими людьми.',
            'Всегда': {
                'column': 'Default',
                'points': 1
            },
            'Часто': {
                'column': 'Default',
                'points': 2
            },
            'Редко': {
                'column': 'Default',
                'points': 3
            },
            'Очень редко': {
                'column': 'Default',
                'points': 4
            },
            'Никогда': {
                'column': 'Default',
                'points': 5
            },
        },
        # 14
        {
            'question': '14. Мне нравится быть с другими людьми.',
            'Всегда': {
                'column': 'Default',
                'points': 5
            },
            'Часто': {
                'column': 'Default',
                'points': 4
            },
            'Редко': {
                'column': 'Default',
                'points': 3
            },
            'Очень редко': {
                'column': 'Default',
                'points': 2
            },
            'Никогда': {
                'column': 'Default',
                'points': 1
            },
        },
        # 15
        {
            'question': '15. Каждый хочет быть приятным для другого.',
            'Всегда': {
                'column': 'Default',
                'points': 1
            },
            'Часто': {
                'column': 'Default',
                'points': 2
            },
            'Редко': {
                'column': 'Default',
                'points': 3
            },
            'Очень редко': {
                'column': 'Default',
                'points': 4
            },
            'Никогда': {
                'column': 'Default',
                'points': 5
            },
        },
        # 16
        {
            'question': '16. Чаще всего люди недовольны собой.',
            'Всегда': {
                'column': 'Default',
                'points': 5
            },
            'Часто': {
                'column': 'Default',
                'points': 4
            },
            'Редко': {
                'column': 'Default',
                'points': 3
            },
            'Очень редко': {
                'column': 'Default',
                'points': 2
            },
            'Никогда': {
                'column': 'Default',
                'points': 1
            },
        },
        # 17
        {
            'question': '17. Большинство людей глупы и непоследовательны.',
            'Всегда': {
                'column': 'Default',
                'points': 5
            },
            'Часто': {
                'column': 'Default',
                'points': 4
            },
            'Редко': {
                'column': 'Default',
                'points': 3
            },
            'Очень редко': {
                'column': 'Default',
                'points': 2
            },
            'Никогда': {
                'column': 'Default',
                'points': 1
            },
        },
        # 18
        {
            'question': '18. Мне нравится быть с людьми, чьи взгляды отличаются от моих.',
            'Всегда': {
                'column': 'Default',
                'points': 1
            },
            'Часто': {
                'column': 'Default',
                'points': 2
            },
            'Редко': {
                'column': 'Default',
                'points': 3
            },
            'Очень редко': {
                'column': 'Default',
                'points': 4
            },
            'Никогда': {
                'column': 'Default',
                'points': 5
            },
        },
    ]

    @classmethod
    def end(cls, vk, profile):
        data = get_data(profile)
        score = data.get('Default', 0)

        message = ''
        attachment = None

        if score <= 30:
            message = 'У вас низкий уровень принятия других людей. Вы критически относитесь к людям, часто раздражаетесь, испытываете презрение по отношению к ним, ожидаете негативного отношения к себе.'
            attachment = 'photo-88277426_457239024'
        elif 31 <= score <= 45:
            message = 'У вас средний уровень принятия других с тенденцией к низкому. Вы испытываете ко многим окружающим неприязнь и ждёте от них подобного же отношения к себе, хотя в Вашем окружении есть отдельные люди, которым вы доверяете.'
            attachment = 'photo-88277426_457239023'
        elif 46 <= score <= 60:
            message = 'У вас средний уровень принятия других с тенденцией к высокому. Вы в целом одобряете окружающих, хотя делаете это избирательно и по отношению к отдельным людям испытываете недоверие.'
            attachment = 'photo-88277426_457239021'
        else:
            message = 'У вас высокий уровень принятия. Вы одобряете жизнь других людей и их отношение к себе в целом, ожидаете позитивное отношение к себе окружающих.'
            attachment = 'photo-88277426_457239022'

        cls.send_end(vk, profile, message, attachment)


# Готов к студенчеству?
class ReadyForTheStudentBodyQuest(QuestBase):
    title = 'Готов к студенчеству?'
    color = VkKeyboardColor.PRIMARY
    greetings = """Совсем скоро ты откроешь для себя новый мир студенчества. А насколько ты готов к жизни в нём? Пройди тест и узнай!"""
    columns = ['Default']
    steps = [
        # 1
        {
            'question': '1.	Что такое альма-матер? ',
            'attachment': 'photo-88277426_457239035',
            'физический термин': {
                'column': 'Default',
                'points': 0
            },
            'старинное название университета': {
                'column': 'Default',
                'points': 2
            },
            'что-то связано с матерью, да?': {
                'column': 'Default',
                'points': 0
            },
        },
        # 2
        {
            'question': '2.	Как у студентов называются занятия?',
            'attachment': 'photo-88277426_457239043',
            'урок': {
                'column': 'Default',
                'points': 0
            },
            'пара': {
                'column': 'Default',
                'points': 2
            },
            'конференция': {
                'column': 'Default',
                'points': 0
            },
        },
        # 3
        {
            'question': '3.	За твоей группой закрепили преподавателя. Как он называется?',
            'attachment': 'photo-88277426_457239047',
            'классный руководитель': {
                'column': 'Default',
                'points': 0
            },
            'воспитатель': {
                'column': 'Default',
                'points': 0
            },
            'куратор': {
                'column': 'Default',
                'points': 2
            },
        },
        # 4
        {
            'question': '4.	Сколько занятий в день у студента вуза?',
            'attachment': 'photo-88277426_457239044',
            '2-3 пары': {
                'column': 'Default',
                'points': 1
            },
            'зависит от факультета': {
                'column': 'Default',
                'points': 0
            },
            'не больше 5 пар': {
                'column': 'Default',
                'points': 2
            },
        },
        # 5
        {
            'question': '5.	В расписании занятий стоят значки * или **. Что они означают?',
            'attachment': 'photo-88277426_457239042',
            'сноска, примечание': {
                'column': 'Default',
                'points': 0
            },
            'фаза луны': {
                'column': 'Default',
                'points': 0
            },
            'четная или нечетная неделя': {
                'column': 'Default',
                'points': 2
            },
        },
        # 6
        {
            'question': '6.	Как называется “студенческий дневник” с оценками?',
            'attachment': 'photo-88277426_457239036',
            'студенческий билет': {
                'column': 'Default',
                'points': 0
            },
            'зачётная книжка': {
                'column': 'Default',
                'points': 2
            },
            'диплом': {
                'column': 'Default',
                'points': 0
            },
        },
        # 7
        {
            'question': '7.	Какую стипендию получают первокурсники в сентябре?',
            'attachment': 'photo-88277426_457239048',
            'не получают, ведь сессии еще не было': {
                'column': 'Default',
                'points': 0
            },
            'получают все одинаково – 2000 рублей': {
                'column': 'Default',
                'points': 2
            },
            'зависит от баллов ЕГЭ при поступлении': {
                'column': 'Default',
                'points': 0
            },
        },
        # 8
        {
            'question': '8.	Сколько сессий в вузе?',
            'attachment': 'photo-88277426_457239038',
            'а что это?': {
                'column': 'Default',
                'points': 1
            },
            'одна - летом': {
                'column': 'Default',
                'points': 0
            },
            'две - в конце каждого семестра': {
                'column': 'Default',
                'points': 2
            },
        },
        # 9
        {
            'question': '9.	Сможешь ли ты, будучи студентом, бесплатно ездить в транспорте, как это было в школе?',
            'attachment': 'photo-88277426_457239040',
            'думаю, да': {
                'column': 'Default',
                'points': 1
            },
            'нет, я же не школьник': {
                'column': 'Default',
                'points': 0
            },
            'наверное, со скидкой': {
                'column': 'Default',
                'points': 2
            },
        },
        # 10
        {
            'question': '10. Что ты наденешь на учебу в вузе?',
            'attachment': 'photo-88277426_457239045',
            'что-нибудь официальное': {
                'column': 'Default',
                'points': 1
            },
            'что-нибудь аккуратное и неброское': {
                'column': 'Default',
                'points': 2
            },
            'я люблю спортивный стиль одежды': {
                'column': 'Default',
                'points': 0
            },
        },
        # 11
        {
            'question': '11. Знаешь ли ты, за что студента могут отчислить из вуза?',
            'attachment': 'photo-88277426_457239039',
            'если завалил экзамены': {
                'column': 'Default',
                'points': 2
            },
            'если пропустил пять занятий': {
                'column': 'Default',
                'points': 0
            },
            'за опоздания': {
                'column': 'Default',
                'points': 0
            },
        },
        # 12
        {
            'question': '12. Куда можно обратиться за юридической, материальной и социальной поддержкой?',
            'attachment': 'photo-88277426_457239041',
            'в Профком обучающихся': {
                'column': 'Default',
                'points': 2
            },
            'в Студенческий совет': {
                'column': 'Default',
                'points': 1
            },
            'к ректору': {
                'column': 'Default',
                'points': 1
            },
        },
    ]

    @classmethod
    def end(cls, vk, profile):
        data = get_data(profile)
        score = data.get('Default', 0)

        message = ''
        attachment = None
        if score <= 15:
            message = 'Хороший результат! Тебя ждет много нового и интересного в ЧувГУ!'
            attachment = 'photo-88277426_457239034'
        elif 16 <= score <= 19:
            message = 'Отличный результат! Ты точно готов стать студентом ЧувГУ!'
            attachment = 'photo-88277426_457239046'
        else:
            message = 'А ты точно абитуриент? Прекрасный результат! Ждем тебя в ЧувГУ!'
            attachment = 'photo-88277426_457239037'

        message = 'Баллов: {0}. {1}'.format(score, message)
        cls.send_end(vk, profile, message, attachment)
