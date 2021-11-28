import logging

from ninja import NinjaAPI

from core.decor import SafeWrapper
from hr_analytics.logic import filter_list, filter_values
from hr_analytics.models import Company, Employee
from hr_analytics.schemas import CompanyGetSchema, EmployeeSchema, EmployeeCreateSchema, EmployeeUpdateSchema, \
    EmployeeGetSchema, FilterValuesSchema, FilterSimpleSchema

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
    employees = map(
        lambda e: dict(
            name=e.name,
            post=e.post,
            education=e.education,
            experience=e.experience,
            date_of_birth=e.date_of_birth,
            sex=e.sex,
            family_status=e.family_status,
            date_of_receipt=e.date_of_receipt,
            date_of_dismissal=e.date_of_dismissal,
            salary=e.salary,
            reason_for_dismissal=e.reason_for_dismissal,
        ),
        employees
    )
    return dict(employees=list(employees))


# UPDATE
@api.post('/employee/update')
@SafeWrapper(EmployeeUpdateSchema)
def employee_update(obj: EmployeeUpdateSchema):
    Employee.objects.update_or_create(obj.dict(), guid=obj.guid)
    return dict()


# DELETE
@api.post('/employee/delete')
@SafeWrapper(EmployeeGetSchema)
def employee_delete(obj: EmployeeGetSchema):
    Employee.objects.filter(guid=obj.guid).delete()
    return dict()


# SELECTION API #
@api.post('/selection/filters')
@SafeWrapper()
def selection_filters():
    """ List[(filter, verbose)] """
    return dict(result=filter_list())


@api.post('/selection/filters/values')
@SafeWrapper(FilterValuesSchema)
def selection_filters_values(obj: FilterValuesSchema):
    """ List[filter_values] """
    return dict(result=filter_values(obj.filter))


@api.post('/selection/filters/simple')
@SafeWrapper(FilterSimpleSchema)
def selection_filters_simple(obj: FilterSimpleSchema):
    f = {obj.filter: obj.value}
    employees = Employee.objects.filter(**f)
    employees = map(
        lambda e: dict(
            name=e.name,
            post=e.post,
            education=e.education,
            experience=e.experience,
            date_of_birth=e.date_of_birth,
            sex=e.sex,
            family_status=e.family_status,
            date_of_receipt=e.date_of_receipt,
            date_of_dismissal=e.date_of_dismissal,
            salary=e.salary,
            reason_for_dismissal=e.reason_for_dismissal,
        ),
        employees
    )
    return dict(result=employees)
