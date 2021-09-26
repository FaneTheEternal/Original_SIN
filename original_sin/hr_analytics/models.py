from django.db import models

from core.mixins.models import GlobalIdentityMixin, TimestampMixin


class Company(GlobalIdentityMixin, TimestampMixin, models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=1024,
    )

    def __str__(self):
        return self.name


class Employee(GlobalIdentityMixin, TimestampMixin, models.Model):
    company = models.ForeignKey(
        to=Company,
        related_name='employees',
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        verbose_name='Имя',
        max_length=1024,
    )
    post = models.CharField(
        verbose_name='Должность',
        max_length=1024,
    )
    education = models.CharField(
        verbose_name='Образование',
        max_length=1024,
    )
    experience = models.PositiveIntegerField(
        verbose_name='Опыт работы (мес.)',
    )
    date_of_birth = models.DateField(
        verbose_name='Дата рождения',
    )
    MAN = 'man'
    FEMALE = 'female'
    OTHER = 'other'
    SEX_KIND = (
        (MAN, 'М'),
        (FEMALE, 'Ж'),
        (OTHER, 'Другое'),
    )
    sex = models.CharField(
        verbose_name='Пол',
        choices=SEX_KIND,
        max_length=1024,
    )
    family_status = models.CharField(
        verbose_name='Семейное положение',
        max_length=1024,
    )
    date_of_receipt = models.DateField(
        verbose_name='Дата приема',
    )
    date_of_dismissal = models.DateField(
        verbose_name='Дата увольнения',
        null=True, blank=True,
    )
    salary = models.PositiveIntegerField(
        verbose_name='Оклад',
    )
    reason_for_dismissal = models.TextField(
        verbose_name='Причина увольнения',
        null=True, blank=True,
    )

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def __str__(self):
        return f'{self.company}: {self.name}'


class Vacation(models.Model):
    employee = models.ForeignKey(
        to=Employee,
        on_delete=models.CASCADE,
        related_name='vacations'
    )
    reason = models.TextField(
        verbose_name='Причика',
    )
    date_start = models.DateField(
        verbose_name='Дата начала',
    )
    date_end = models.DateField(
        verbose_name='Дата окончания',
        null=True, blank=True,
    )

    class Meta:
        verbose_name = 'Опуск'
        verbose_name_plural = 'Отпуска'
