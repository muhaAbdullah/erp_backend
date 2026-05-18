"""
HRM Views.
"""
from .employee import EmployeeViewSet
from .employee_personal import EmployeePersonalViewSet
from .employee_contact import EmployeeContactViewSet
from .employee_government import EmployeeGovernmentViewSet
from .master_views import (
    DepartmentViewSet, DesignationViewSet, ShiftViewSet,
    EmployeeTypeViewSet, ScaleCategoryViewSet
)
from .global_views import ReligionViewSet, QualificationViewSet

__all__ = [
    'EmployeeViewSet',
    'EmployeePersonalViewSet',
    'EmployeeContactViewSet',
    'EmployeeGovernmentViewSet',
    'DepartmentViewSet',
    'DesignationViewSet',
    'ShiftViewSet',
    'EmployeeTypeViewSet',
    'ScaleCategoryViewSet',
    'ReligionViewSet',
    'QualificationViewSet',
]
