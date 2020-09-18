from django.db import models

from schedule.models.catalog import Teacher, Discipline, LectureHall, Institute


class Schedule(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=30,
        null=True, blank=True,
    )

    institute = models.ForeignKey(
        to=Institute,
        on_delete=models.CASCADE,
        related_name='schedules'
    )

    group = models.CharField(
        verbose_name='Группа',
        max_length=20,
    )


class Subject(models.Model):
    schedule = models.ForeignKey(
        to=Schedule,
        on_delete=models.CASCADE,
        related_name='subjects'
    )

    teacher = models.ForeignKey(
        to=Teacher,
        on_delete=models.SET_NULL,
        related_name='subjects',
        null=True, blank=True,
    )

    discipline = models.ForeignKey(
        to=Discipline,
        on_delete=models.CASCADE,
        related_name='subjects',
    )

    lecture_hall = models.ForeignKey(
        to=LectureHall,
        on_delete=models.SET_NULL,
        related_name='subjects',
        null=True, blank=True,
    )

    LECTURE = 'лк'
    PRACTICE = 'пр'
    LABORATORY = 'лб'
    TYPES = [LECTURE, PRACTICE, LABORATORY]
    TYPES = zip(TYPES, TYPES)
    type = models.CharField(
        verbose_name='Тип',
        choices=TYPES,
        max_length=10,
        null=True, blank=True
    )

    position = models.IntegerField(
        verbose_name='Порядковый номер',
    )

    day = models.IntegerField(
        verbose_name='День недели'
    )

    is_even = models.BooleanField(
        verbose_name='Четный ли',
        null=True, blank=True,
    )
