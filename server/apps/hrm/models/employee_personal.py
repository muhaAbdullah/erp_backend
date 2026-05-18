from django.db import models
from coresite.mixin.basemodel import BaseModel
from .employee import Employee
from .religion import Religion
from .qualification import Qualification


class EmployeePersonal(BaseModel):
    """
    Employee Personal Information model with multi-tenant isolation.
    
    Stores personal and family details for employees.
    Inherits from BaseModel to ensure organization-level tenant isolation.
    
    Features:
    - Family member information (father, mother)
    - Marital status tracking
    - Blood group and medical information
    - Nationality and religious information
    """
    
    # Marital status choices
    MARITAL_STATUS_CHOICES = [
        ('SINGLE', 'Single'),
        ('MARRIED', 'Married'),
        ('DIVORCED', 'Divorced'),
        ('WIDOWED', 'Widowed'),
    ]
    
    # Blood group choices
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
    ]
    
    employee = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        related_name='personal_info',
        help_text="Employee this personal information belongs to"
    )
    father_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Father's full name"
    )
    mother_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Mother's full name"
    )
    marital_status = models.CharField(
        max_length=20,
        choices=MARITAL_STATUS_CHOICES,
        blank=True,
        help_text="Current marital status"
    )
    blood_group = models.CharField(
        max_length=5,
        choices=BLOOD_GROUP_CHOICES,
        blank=True,
        help_text="Blood group type"
    )
    nationality = models.CharField(
        max_length=50,
        blank=True,
        help_text="Nationality/citizenship"
    )
    
    # Master data relationships
    religion = models.ForeignKey(
        Religion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
        help_text="Religious affiliation from global master data"
    )
    qualification = models.ForeignKey(
        Qualification,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
        help_text="Highest educational qualification from global master data"
    )
    
    class Meta:
        verbose_name = 'Employee Personal Information'
        verbose_name_plural = 'Employee Personal Information'
        indexes = [
            models.Index(fields=['organization', 'employee']),
        ]
    
    def __str__(self):
        """Return employee code with personal info label for admin readability."""
        return f"Personal Info - {self.employee.employee_code}"
