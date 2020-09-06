import uuid

from django.db import models


class ChatStep(models.Model):
    code = models.UUIDField(
        verbose_name='Код для индефикации',
        default=uuid.uuid4
    )
    message = models.TextField(
        verbose_name='Сообщение'
    )
    actions = models.ManyToManyField(
        to='self',
        through='ProxyStep'
    )
    index = models.BooleanField(
        verbose_name='Домашний шаг',
        default=False
    )


class ProxyStep(models.Model):
    on = models.ForeignKey(
        to=ChatStep,
        on_delete=models.CASCADE,
        related_name='on_proxy',
    )
    to = models.ForeignKey(
        to=ChatStep,
        on_delete=models.CASCADE,
        related_name='to_proxy',
    )
    title = models.CharField(
        verbose_name='Сообщение для перехода',
        max_length=40
    )
    JUMP = 'jump'
    MSG = 'msg'
    QUEST = 'quest'
    HOME = 'home'
    TYPES = [JUMP, MSG, QUEST, HOME]
    TYPES = zip(TYPES, TYPES)
    type = models.CharField(
        verbose_name='Тип шага',
        choices=TYPES,
        max_length=10
    )
