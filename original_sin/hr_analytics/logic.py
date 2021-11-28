import logging
import re
from pathlib import Path

import pandas as pd
import numpy as np
from django.conf import settings

from hr_analytics.models import Company, Employee

logger = logging.getLogger(__name__)


def import_employees():
    file = getattr(settings, 'BASE_DIR')
    file = Path(file).joinpath('analytics_data.xlsx')
    xl = pd.ExcelFile(file)
    company = Company.objects.get(name='CompanyDefault')
    rows = xl.parse('1').iterrows()
    count_all = 0
    count_new = 0
    for index, row in list(rows)[2:]:  # pass headers
        # fix nan
        row = list(map(lambda x: x if x is not np.nan else None, row))
        logging.info(list(row))
        name, post, date_of_birth, sex, family_status, date_of_receipt = row[:6]
        date_of_dismissal = row[6]
        salary = row[9]
        obj = dict(
            company=company,
            name=name,
            post=post,
            education='-',
            experience=0,
            date_of_birth=date_of_birth,
            sex=Employee.FEMALE if sex == 'женский' else Employee.MAN,
            family_status=family_status,
            date_of_receipt=date_of_receipt,
            date_of_dismissal=date_of_dismissal,
            salary=salary,
        )
        count_all += 1
        o, created = Employee.objects.get_or_create(
            obj,
            company=company,
            name=name,
            date_of_birth=date_of_birth,
            date_of_receipt=date_of_receipt,
        )
        if created:
            count_new += 1
    logger.info(f'Processed: {count_all}; New: {count_new}')


def filter_list():
    """ allowed filters """
    filters = [
        'name',
        'post',
        'education',
        'experience',
        'date_of_birth',
        'sex',
        'family_status',
        'date_of_receipt',
        'date_of_dismissal',
        'salary',
        'reason_for_dismissal',
    ]
    filters = [
        (field.name, field.verbose_name)
        for field in Employee._meta.get_fields()
        if field.name in filters
    ]
    return filters


def filter_values(f: str) -> list:
    values = Employee.objects.all().values_list(f, flat=True)
    return list(set(values))
