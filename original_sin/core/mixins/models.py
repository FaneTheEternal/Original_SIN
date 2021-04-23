import uuid

from django.db import models


class GlobalIdentityMixin(models.Model):
    guid = models.UUIDField(
        verbose_name='Code',
        db_index=True,
        default=uuid.uuid4,
        editable=False,
    )

    class Meta:
        abstract = True


class UniqueMixin(models.Model):
    uid = models.UUIDField(
        verbose_name='UUID4',
        default=uuid.uuid4,
        editable=False,
        db_index=True,
    )

    class Meta:
        abstract = True


class TimestampMixin(models.Model):
    created = models.DateTimeField(
        verbose_name='Создано',
        auto_now_add=True,
    )
    modified = models.DateTimeField(
        verbose_name='Обновлено',
        auto_now=True,
    )

    class Meta:
        abstract = True
