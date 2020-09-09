import subprocess
import platform
import sys

import requests
from bs4 import BeautifulSoup

from .consts import CHUVSU_SCHEDULE_DOMAIN
from .models import Schedule, Institute


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


class NotScheduleException(Exception):
    pass


class ScheduleBackend(object):
    CANT_PING_MSG = 'Chuvsu schedule server unavailable'

    parse_range = range(4700, 5900)
    url_mask = '/index/grouptt/gr/{group_num}'
    protocol = 'https://'

    is_even = None

    def __init__(self):
        is_active = ping(CHUVSU_SCHEDULE_DOMAIN)
        if not is_active:
            print(self.CANT_PING_MSG, file=sys.stderr)
            return
        self.institute = Institute.objects.get(short_name='ЧувГУ')

    def test(self, num):
        return self._update_for(num)

    def _update_for(self, num: int):
        url = self.protocol + CHUVSU_SCHEDULE_DOMAIN + self.url_mask.format(group_num=num)
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        data_table = soup.find(id='groupstt')
        if not data_table:
            raise NotScheduleException

        group = soup.find('span', {'class': 'htext'}).span.string
        schedule, _ = Schedule.objects.get_or_create(
            institute=self.institute,
            group=group
        )

    def update(self):
        for num in self.parse_range:
            try:
                self._update_for(num)
            except NotScheduleException:
                pass
            except Exception as e:
                print(e, file=sys.stderr)
