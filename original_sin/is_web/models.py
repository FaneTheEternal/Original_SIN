from django.db import models

from core.mixins.models import TimestampMixin, UniqueMixin


def gen_card_img_path(instance, filename):
    return f'{instance.__class__.__name__.lower()}/{instance.uid}/{filename}'


class CardAbstract(UniqueMixin, TimestampMixin, models.Model):
    header = models.CharField(
        verbose_name='Заголовок',
        max_length=1024,
        null=True, blank=True,
    )
    title = models.CharField(
        verbose_name='Название',
        max_length=1024,
        null=True, blank=True,
    )
    LINKS_SEPARATOR = '||'
    LINK_CONTENT_SEPARATOR = '|~|'
    links = models.TextField(
        verbose_name='Ссылки',
        null=True, blank=True,
    )
    text = models.TextField(
        verbose_name='Текст',
        null=True, blank=True,
    )
    img = models.ImageField(
        verbose_name='Каринка',
        null=True, blank=True,
        upload_to=gen_card_img_path,
    )

    class Meta:
        abstract = True

    def __str__(self):
        s = []
        if self.header or self.title:
            if self.header:
                s.append(self.header)
            if self.title:
                s.append(self.title)
        else:
            s.extend([self._meta.verbose_name, str(self.pk)])
        return ': '.join(s)

    def get_links(self):
        if not self.links:
            return []
        links = self.links.split(self.LINKS_SEPARATOR)
        links = map(lambda x: x.split(self.LINK_CONTENT_SEPARATOR), links)
        return links


class News(CardAbstract):
    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'


class CatalogItem(CardAbstract):
    class Meta:
        verbose_name = 'Пункт каталога'
        verbose_name_plural = 'Пункты каталога'
