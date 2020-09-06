from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import BotProfile

from .step import ProxyStep
from ..utils import home_code


class VkUser(BotProfile):
    position = models.UUIDField(
        verbose_name='Код текущего шага',
        default=home_code
    )

    def set_home(self):
        proxy = ProxyStep.objects.get(type=ProxyStep.HOME)
        self.position = proxy.to.code
        self.save()


class QuestProfile(models.Model):
    """ Профиль в 'квестах' """
    user = models.OneToOneField(
        to=VkUser,
        on_delete=models.CASCADE,
        related_name='quest_profile',
    )
    data = models.TextField(
        verbose_name='JSON данные',
        default='{}'
    )

    @receiver(post_save, sender=VkUser)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            QuestProfile.objects.create(user=instance)

    @receiver(post_save, sender=VkUser)
    def save_user_profile(sender, instance, **kwargs):
        instance.quest_profile.save()
