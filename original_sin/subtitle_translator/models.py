from django.db import models

from core.mixins.models import UniqueMixin


def gen_file_path(instance, filename):
    return f'simple_user/{instance.uid}/sources/{filename}'


def gen_res_path(instance, filename):
    return f'simple_user/{instance.uid}/results/{filename}'


class SimpleUser(UniqueMixin, models.Model):
    file = models.FileField(
        verbose_name='Файл сабов',
        null=True, blank=True,
        upload_to=gen_file_path,
    )
    translators_cache = models.JSONField(
        verbose_name='Результаты от переводчиков',
        null=True, blank=True,
    )
    parser = models.CharField(
        verbose_name='Parser class name',
        max_length=100,
        null=True, blank=True,
    )
    translators = models.JSONField(
        verbose_name='List[str] of translators class name',
        null=True, blank=True,
    )
    translators_params = models.JSONField(
        verbose_name='Translators kwargs',
        null=True, blank=True,
    )
    file_result = models.FileField(
        verbose_name='Результат',
        null=True, blank=True,
        upload_to=gen_res_path,
    )


class NameLessFile(models.Model):
    hash = models.CharField(
        verbose_name='SHA256',
        max_length=100,
    )
    file = models.FileField()
