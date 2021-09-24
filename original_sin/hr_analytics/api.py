import logging

from ninja import NinjaAPI

from core.decor import SafeWrapper
from hr_analytics.models import Company, Employee
from hr_analytics.schemas import CompanyGetSchema, EmployeeSchema, EmployeeCreateSchema

api = NinjaAPI(urls_namespace='hr_analytics')

logger = logging.getLogger(__name__)


@api.post('/default')
@SafeWrapper()
def default():
    return dict(company=Company.objects.get(name='CompanyDefault').guid)


#  # CRUD
# CREATE
@api.post('/employee/create')
@SafeWrapper(EmployeeCreateSchema)
def employee_create(obj: EmployeeCreateSchema):
    company = Company.objects.get(guid=obj.company)
    employee = Employee(
        company=company,
        name=obj.name,
        education=obj.education,
        experience=obj.experience,
        date_of_birth=obj.date_of_birth,
        sex=obj.sex,
        family_status=obj.family_status,
        date_of_receipt=obj.date_of_receipt,
        date_of_dismissal=obj.date_of_dismissal,
        salary=obj.salary,
        reason_for_dismissal=obj.reason_for_dismissal,
    )
    employee.save()
    return dict()


# SELECT
@api.post('/employee/all')
@SafeWrapper(CompanyGetSchema)
def employee_all(obj: CompanyGetSchema):
    company = Company.objects.get(guid=obj.guid)
    employees = company.employees.all()
    employees = map(lambda e: EmployeeSchema.from_django(e), employees)
    return dict(employees=employees)
