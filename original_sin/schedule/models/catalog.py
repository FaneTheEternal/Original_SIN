from django.db import models


class Institute(models.Model):
    short_name = models.CharField(
        verbose_name='Сокращение',
        max_length=30,
    )

    full_name = models.CharField(
        verbose_name='Полное название',
        max_length=100,
    )

    def __str__(self):
        return self.short_name


class InstituteSlaveMixin(models.Model):
    name = ''  # must be models.CharField
    RELATED_NAME = '+'

    institute = models.ForeignKey(
        to=Institute,
        on_delete=models.CASCADE,
        related_name=RELATED_NAME
    )

    def __str__(self):
        return f'{self.name} {self.institute}'

    class Meta:
        abstract = True


class Teacher(InstituteSlaveMixin, models.Model):
    RELATED_NAME = 'teachers'

    name = models.CharField(
        verbose_name='Имя',
        max_length=50,
    )

    prefix = models.CharField(
        verbose_name='Префикс',
        max_length=100,
        null=True, blank=True,
    )

    @property
    def name_with_prefix(self):
        if self.prefix:
            return f'{self.prefix} {self.name}'
        return self.name

    @property
    def full_name(self):
        return f'{self.name_with_prefix} f{self.institute}'


class Discipline(InstituteSlaveMixin, models.Model):
    RELATED_NAME = 'disciplines'

    name = models.CharField(
        verbose_name='Название',
        max_length=100,
    )


class LectureHall(InstituteSlaveMixin, models.Model):
    RELATED_NAME = 'lecture_halls'

    name = models.CharField(
        verbose_name='Название',
        max_length=50
    )
