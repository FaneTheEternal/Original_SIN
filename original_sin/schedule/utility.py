import subprocess
import platform
import sys
from collections import Iterable

from .models import Schedule, Institute, Subject


def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.

    https://stackoverflow.com/a/32684938/12760088
    """

    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower() == 'windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]

    return subprocess.call(command) == 0


def num_by_day_name(name: str):
    week = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    try:
        if not isinstance(name, str):
            raise ValueError

        return week.index(name)
    except ValueError:
        return None


def iterable(obj):
    try:
        iter(obj)
    except Exception:
        return False
    else:
        return True


def flatten(obj):
    if iterable(obj):
        flat = []
        for o in obj:
            if iterable(o):
                flat += flatten(o)
            else:
                flat.append(o)
        return flat
    return obj


class NotScheduleException(Exception):
    pass


class ParserOld(object):
    HOST_NAME = None
    INSTITUTE_NAME = None
    DOMAIN = None

    data = []

    @property
    def CANT_PING_MSG(self):
        return f'${self.HOST_NAME} schedule server unavailable'

    def __init__(self):
        self._implement_check()

        is_active = ping(self.DOMAIN)
        if not is_active:
            print(self.CANT_PING_MSG, file=sys.stderr)
            return
        self.institute = Institute.objects.get(short_name=self.INSTITUTE_NAME)

    def _implement_check(self):
        status = True
        status &= self.HOST_NAME is not None
        status &= self.INSTITUTE_NAME is not None
        status &= self.DOMAIN is not None
        if not status:
            raise NotImplementedError

    def test(self):
        raise NotImplementedError

    def _execute(self):
        raise NotImplementedError

    def save(self):
        if len(self.data) == 0:
            raise NotScheduleException(f'Нет расписания для ${self.INSTITUTE_NAME}')
        try:
            schedule, subjects = self.data[0]
            assert isinstance(schedule, Schedule)
            assert isinstance(subjects, list)
            assert isinstance(subjects[0], Subject)
        except [ValueError, AssertionError, IndexError]:
            raise Exception('Не верный формат данных')

        schedules = []
        subjects = []
        for schedule, subjects in self.data:
            schedules.append(schedule)
            subjects += subjects

        old_schedule = Schedule.objects.filter(institute=self.institute)
        Subject.objects.filter(schedule__in=old_schedule).delete()
        old_schedule.delete()

        Schedule.objects.bulk_create(schedules, batch_size=50)
        Subject.objects.bulk_create(subjects, batch_size=20)

    def invoke(self):
        self._execute()
        self.save()
