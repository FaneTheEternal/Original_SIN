import re
import sys

import requests
from bs4 import BeautifulSoup

from schedule.consts import CHUVSU_SCHEDULE_DOMAIN
from schedule.models import LectureHall, Discipline, Teacher, Institute, Schedule, Subject
from schedule.utility import ParserOld, num_by_day_name, ping, NotScheduleException


class ChyvsuParser(object):
    def __init__(self):
        self.subject_re = re.compile(r'(?P<even>\*|\*\*)?'
                                     r'(?P<lecture_hall>([А-Я]-[0-9]+)|(База кафедры))?\s?'
                                     r'(?P<discipline>[а-яА-Яa-zA-Z ,.()-]+)\s?'
                                     r'\((?P<type>пр|лб|лк)\)\s?'
                                     r'(?P<weeks>(\([0-9]-[0-9]+ нед.\) )|(\([0-9]+ нед.\) ))?'
                                     r'(?P<prefix>[а-я .-]+)?\s?'
                                     r'(?P<teacher>[А-Я][а-я]+ [А-Я]. [А-Я].)?\s?'
                                     r'(?P<subgroup>[0-9] подгруппа)?\s?'
                                     r'(?P<dot>\(ДОТ\))?')
        self.soup = None
        self.group = None

        self.in_assembly = False
        self.assembly_data = None

    def _parse(self):
        data_table = self.soup.find(id='groupstt')

        if not data_table:
            raise NotScheduleException

        data_table = data_table.tbody

        group_name = self.soup.find('span', {'class': 'htext'}).span.string
        is_divide = any(self.soup.find_all('i', string='1 подгруппа'))
        group = {
            'name': group_name
        }

        subjects = []

        day_name = ''

        for el in data_table.find_all('tr', recursive=False):
            el_class = el.get('class', None)
            if el_class is not None and 'trfd' in el_class:
                day_name = el.find('td').string
            else:
                if el.get_text().strip() == 'День самостоятельной работы':
                    continue
                position = el.find('td', {'class': ['trf', 'trdata']})
                position = position.div.get_text()
                position = int(position[0])  # roflan re

                data = el.find('div', {'class': 'tdd'})
                data = data.table
                if data is None:
                    continue

                for row in data.find_all('tr'):
                    subject = {
                        'teacher': {},
                        'discipline': {},
                        'lecture_hall': {},
                        'type': str,
                        'position': position,
                        'day': int,
                        'is_even': bool,
                        'subgroup': None
                    }

                    row = row.get_text()

                    match = self.subject_re.match(row)
                    # print(row, bool(match))
                    match = match.groupdict()

                    teacher = match.get('teacher', None)
                    prefix = match.get('prefix', None)
                    if prefix:
                        prefix = prefix.strip()
                    subject['teacher'] = dict(name=teacher.strip(), prefix=prefix) if teacher else None

                    discipline = match.get('discipline')
                    subject['discipline'] = dict(name=discipline.strip())

                    lecture_hall = match.get('lecture_hall', None)
                    subject['lecture_hall'] = dict(name=lecture_hall.strip()) if lecture_hall else None

                    _type = match.get('type')
                    subject['type'] = _type.strip()

                    day_num = num_by_day_name(day_name)
                    subject['day'] = day_num

                    is_even = match.get('even', None)
                    subject['is_even'] = is_even == '**' if is_even is not None else None

                    subgroup = match.get('subgroup', None)
                    if subgroup is not None:
                        subject['subgroup'] = subgroup.strip()

                    subjects.append(subject)

        if is_divide:
            subgroups = {}  # {name1: data1 ,name2: data2}
            neutral = []
            for subject in subjects:
                subgroup = subject.get('subgroup')
                if subgroup is None:
                    neutral.append(subject)
                else:
                    sub = subgroups.get(subgroup, None) or []
                    subgroups[subgroup] = sub + [subject]
            group['subgroups'] = [
                {
                    'name': name,
                    'data': (data or []) + (neutral or [])
                }
                for name, data in subgroups.items()
            ]
        else:
            group['data'] = subjects

        self.group = group

    def invoke(self, page):
        self.soup = BeautifulSoup(page, 'html.parser')
        self._parse()

    def flush(self):
        self.group = None

    @property
    def data(self):
        return self.group


class ScheduleBackend(object):
    def __init__(self):
        self.domain = CHUVSU_SCHEDULE_DOMAIN

        is_active = ping(self.domain)
        if not is_active:
            raise Exception('Scheduler offline')

        self.url = 'https://' + CHUVSU_SCHEDULE_DOMAIN + '/index/grouptt/gr/{num}'
        self.parser = ChyvsuParser()
        self.range = None

        self._institute = 'ЧувГУ'

    def _get_page(self, num):
        response = requests.get(
            url=self.url.format(num=num)
        )
        return response.content

    def clear(self):
        Schedule.objects.all().delete()

    def fill_db(self, on=None, to=None):
        if not (isinstance(on, int) and isinstance(to, int)):
            raise Exception('range should be set (on: int, to: int)')

        def _replace(_rows, _schedule):
            new = []
            for row in _rows:
                row.pop('subgroup', None)
                row['schedule'] = _schedule

                if row['teacher'] is not None and not isinstance(row['teacher'], Teacher):
                    row['teacher'], _ = Teacher.objects.get_or_create(
                        **row['teacher'],
                        institute=self.institute
                    )

                if not isinstance(row['discipline'], Discipline):
                    row['discipline'], _ = Discipline.objects.get_or_create(
                        **row['discipline'],
                        institute=self.institute
                    )

                if row['lecture_hall'] is not None and not isinstance(row['lecture_hall'], LectureHall):
                    row['lecture_hall'], _ = LectureHall.objects.get_or_create(
                        **row['lecture_hall'],
                        institute=self.institute
                    )

                    new.append(Subject(**row))

            return new

        for num in range(on, to):
            print(f'try {num}', end='')
            page = self._get_page(num)
            try:
                self._parse(page)
            except NotScheduleException:
                print(f' pass...')
                pass
            except Exception as e:
                print(f' Error: {e}')
            else:
                print(f' found!')
                parsed = self.data
                gr_name = parsed['name']
                if parsed.get('subgroups', False):
                    subgroups = parsed.get('subgroups')
                    for group in subgroups:
                        schedule = Schedule.objects.create(
                            name=group['name'],
                            institute=self.institute,
                            group=gr_name,
                        )
                        rows = group.get('data')
                        rows = _replace(rows, schedule)
                        news = Subject.objects.bulk_create(rows, batch_size=50)
                        print(f'created {len(news)}')

                else:
                    schedule = Schedule.objects.create(
                        institute=self.institute,
                        group=gr_name,
                    )
                    rows = parsed.get('data')
                    rows = _replace(rows, schedule)
                    news = Subject.objects.bulk_create(rows, batch_size=50)
                    print(f'created {len(news)}')

    def update(self):
        self.clear()
        self.fill_db(
            on=3600,
            to=5900,
        )

    def _parse(self, page):
        self.parser.invoke(page)

    @property
    def institute(self):
        """ Single Institute """
        if not isinstance(self._institute, Institute):
            self._institute = Institute.objects.get(
                short_name=self._institute
            )
        return self._institute

    @property
    def data(self):
        return self.parser.data

    def test(self, num):
        page = self._get_page(num)
        self._parse(page)
        data = self.data
        if data.get('data', None):
            print(len(data.get('data', None)))
        else:
            print([sum([len(j) for j in i.get('data')]) for i in data.get('subgroups', None)])
