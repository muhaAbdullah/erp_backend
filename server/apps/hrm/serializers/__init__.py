"""
HRM Serializers.
"""
from .employee import EmployeeSerializer, EmployeeListSerializer
from .employee_personal import EmployeePersonalSerializer
from .employee_contact import EmployeeContactSerializer
from .employee_government import EmployeeGovernmentSerializer
from .department import DepartmentSerializer
from .designation import DesignationSerializer
from .shift import ShiftSerializer
from .employee_type import EmployeeTypeSerializer
from .scale_category import ScaleCategorySerializer
from .religion import ReligionSerializer
from .qualification import QualificationSerializer

__all__ = [
    'EmployeeSerializer',
    'EmployeeListSerializer',
    'EmployeePersonalSerializer',
    'EmployeeContactSerializer',
    'EmployeeGovernmentSerializer',
    'DepartmentSerializer',
    'DesignationSerializer',
    'ShiftSerializer',
    'EmployeeTypeSerializer',
    'ScaleCategorySerializer',
    'ReligionSerializer',
    'QualificationSerializer',
]
