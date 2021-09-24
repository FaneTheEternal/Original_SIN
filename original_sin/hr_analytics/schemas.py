from djantic import ModelSchema
from ninja import Schema

from . import models


class CompanyGetSchema(Schema):
    guid: str


class EmployeeCreateSchema(ModelSchema):
    company: str

    class Config:
        model = models.Employee
        exclude = ['guid', 'created', 'modified', 'id']


class EmployeeSchema(ModelSchema):
    class Config:
        model = models.Employee
        exclude = ['company']
