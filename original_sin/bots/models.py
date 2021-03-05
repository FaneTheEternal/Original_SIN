from django.db import models

from core.mixins.models import GlobalIdentityMixin


class TelegramUser(GlobalIdentityMixin, models.Model):
    location = models.UUIDField(
        verbose_name='Код текущего шага',
    )


class BotStep(GlobalIdentityMixin, models.Model):
    on = models.ManyToManyField(
        to='self',
        related_name='to',
    )


class BotStepProxy(models.Model):
    on = models.ForeignKey(
        to=BotStep,
        related_name='options',
        on_delete=models.CASCADE,
    )
    to = models.ForeignKey(
        to=BotStep,
        related_name='from_options',
        on_delete=models.CASCADE,
    )
    title = models.CharField(
        verbose_name='Название',
        max_length=1024,
    )
    text = models.TextField(
        verbose_name='Текст',
    )
