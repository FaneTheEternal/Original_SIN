from djantic import ModelSchema
from ninja import Schema

from . import models


class CompanyGetSchema(Schema):
    guid: str


class EmployeeGetSchema(Schema):
    guid: str


class EmployeeCreateSchema(ModelSchema):
    company: str

    class Config:
        model = models.Employee
        exclude = ['guid', 'created', 'modified', 'id']


class EmployeeUpdateSchema(ModelSchema):
    class Config:
        model = models.Employee
        exclude = ['created', 'modified', 'id', 'company']


class EmployeeSchema(ModelSchema):
    class Config:
        model = models.Employee
        exclude = ['company']
