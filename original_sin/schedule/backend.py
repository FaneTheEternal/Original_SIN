import re
import sys

import requests
from bs4 import BeautifulSoup

from schedule.consts import CHUVSU_SCHEDULE_DOMAIN
from schedule.models import LectureHall, Discipline, Teacher
from schedule.utility import ParserOld, NotScheduleException, num_by_day_name, ping


class ChyvsuParser(object):
    def __init__(self):
        self.subject_re = re.compile(r'(?P<even>\*|\*\*)?(?P<lecture_hall>([А-Я]-[0-9]+)|(База кафедры)) '
                                     r'(?P<discipline>[а-яА-Яa-zA-Z ()-]+) \((?P<type>пр|лб|лк)\) '
                                     r'\((?P<weeks>[0-9]-[0-9]+ нед.)\) (?P<prefix>[а-я .-]+)?\s*'
                                     r'(?P<teacher>[А-Я][а-я]+ [А-Я]. [А-Я].)?(?P<subgroup>\s?[0-9] подгруппа)?'
                                     r'(?P<dot>\s*\(ДОТ\))?')
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
                subject = {
                    'teacher': {},
                    'discipline': {},
                    'lecture_hall': {},
                    'type': str,
                    'position': int,
                    'day': int,
                    'is_even': bool,
                    'subgroup': None  # ONLY IF is_divide
                }
                position = el.find('td', {'class': ['trf', 'trdata']})
                position = position.div.get_text()
                position = int(position[0])  # roflan re
                subject['position'] = position

                data = el.find('div', {'class': 'tdd'})
                data = data.table
                if data is None:
                    continue
                data = data.get_text()

                match = self.subject_re.match(data)
                match = match.groupdict()

                teacher = match.get('teacher', None)
                prefix = match.get('prefix', None)
                subject['teacher'] = dict(name=teacher.strip(), prefix=prefix) if teacher else None

                discipline = match.get('discipline')
                subject['discipline'] = dict(name=discipline.strip())

                lecture_hall = match.get('lecture_hall', None)
                subject['lecture_hall'] = dict(name=lecture_hall.strip()) if lecture_hall else None

                _type = match.get('type')
                subject['type'] = _type.strip()

                day_num = num_by_day_name(day_name)
                subject['day'] = day_num

                is_even = match.get('even')
                subject['is_even'] = is_even == '**'

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

    def load(self, pages):
        self.assembly_data = pages
        self.in_assembly = bool(self.assembly_data)

    def assembly(self):
        if not self.in_assembly:
            raise RuntimeError('Not load data to assembly')
        for page in self.assembly_data:
            self.invoke(page)
            data = self.data
            self.flush()
            yield data


class ScheduleBackend(object):
    def __init__(self):
        self.domain = CHUVSU_SCHEDULE_DOMAIN

        is_active = ping(self.domain)
        if not is_active:
            raise Exception('Scheduler offline')

        self.url = 'https://' + CHUVSU_SCHEDULE_DOMAIN + '/index/grouptt/gr/{num}'
        self.parser = ChyvsuParser()
        self.range = None

    def _get_page(self, num):
        response = requests.get(
            url=self.url.format(num=num)
        )
        return response.content

    def fill_db(self, on=None, to=None):
        for num in range(on, to):
            page = self._get_page(num)
            self._parse(page)
            # TODO: Доделать заполнение бд

    def _parse(self, page):
        self.parser.invoke(page)

    @property
    def data(self):
        return self.parser.data

    def test(self, num):
        page = self._get_page(num)
        self._parse(page)
        data = self.data
        print(data)
