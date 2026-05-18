"""
HRM Admin registration.
"""
from .employee_admin import EmployeeAdmin
from .master_admin import (
    DepartmentAdmin, DesignationAdmin, ShiftAdmin,
    EmployeeTypeAdmin, ScaleCategoryAdmin
)
from .global_admin import ReligionAdmin, QualificationAdmin

__all__ = [
    'EmployeeAdmin',
    'DepartmentAdmin',
    'DesignationAdmin',
    'ShiftAdmin',
    'EmployeeTypeAdmin',
    'ScaleCategoryAdmin',
    'ReligionAdmin',
    'QualificationAdmin',
]
