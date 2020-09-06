from django.db import models

# Create your models here.


class BotProfile(models.Model):
    ID_LENGTH = 30

    user_id = models.CharField(
        blank=False, null=False,
        max_length=ID_LENGTH
    )

    class Meta:
        abstract = True

    def __str__(self):
        return '{} <id:{}>'.format(self.__class__.__name__, self.user_id)
