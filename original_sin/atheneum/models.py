import uuid
from typing import Optional

from django.db import models
from ordered_model.models import OrderedModel

from core.mixins.models import UniqueMixin


class SimpleUser(UniqueMixin, models.Model):
    pass


class Book(UniqueMixin, models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=255,
    )
    author = models.CharField(
        verbose_name='Автор',
        max_length=255,
    )

    def __str__(self):
        return self.name

    @property
    def cover(self):
        first: Optional[Page] = self.pages.first()
        return first and first.file

    @property
    def cover_url(self) -> str:
        return self.cover and self.cover.url


def page_filename(instance, filename):
    book = instance.book
    page_name = uuid.uuid4().hex
    ext = filename[filename.rindex('.'):]
    return '/'.join(['books', f'{book.name}_{book.uid}', f'{instance.order}_{page_name}{ext}'])


class Page(OrderedModel):
    book = models.ForeignKey(
        to=Book,
        on_delete=models.CASCADE,
        related_name='pages',
    )
    file = models.FileField(
        verbose_name='Скан',
        null=True, blank=True,
        upload_to=page_filename,
    )
    name = models.CharField(
        verbose_name='Название',
        null=True, blank=True,
        max_length=64,
    )
    order_with_respect_to = 'book'

    class Meta(OrderedModel.Meta):
        ordering = ('book', 'order')
