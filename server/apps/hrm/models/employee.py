from django.db import models
from coresite.mixin.basemodel import BaseModel
from apps.core.models import User
from .department import Department
from .designation import Designation
from .shift import Shift
from .employee_type import EmployeeType
from .scale_category import ScaleCategory


class Employee(BaseModel):
    """
    Core Employee model with multi-tenant isolation.
    
    Inherits from BaseModel to ensure organization-level tenant isolation.
    Each employee record is tied to an organization and can optionally be
    linked to a User account for login capabilities.
    
    Features:
    - Unique employee codes per organization
    - Optional user account linkage for system access
    - Employment status tracking
    - Gender and demographic information
    """
    
    # Gender choices
    GENDER_CHOICES = [
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
    ]
    
    # Employment status choices
    EMPLOYMENT_STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('TERMINATED', 'Terminated'),
        ('RESIGNED', 'Resigned'),
    ]
    
    employee_code = models.CharField(
        max_length=20,
        help_text="Unique employee code within organization"
    )
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employee',
        help_text="Link to user account for login-enabled employees"
    )
    
    # Master data relationships
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
        help_text="Department where the employee works"
    )
    designation = models.ForeignKey(
        Designation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
        help_text="Job title or position of the employee"
    )
    shift = models.ForeignKey(
        Shift,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
        help_text="Working shift assigned to the employee"
    )
    employee_type = models.ForeignKey(
        EmployeeType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
        help_text="Employment type (Permanent, Contract, etc.)"
    )
    scale_category = models.ForeignKey(
        ScaleCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
        help_text="Salary scale or grade category"
    )
    
    first_name = models.CharField(
        max_length=100,
        help_text="Employee's first name"
    )
    middle_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Employee's middle name (optional)"
    )
    last_name = models.CharField(
        max_length=100,
        help_text="Employee's last name"
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        help_text="Employee's date of birth"
    )
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        help_text="Employee's gender"
    )
    joining_date = models.DateField(
        help_text="Date when employee joined the organization"
    )
    employment_status = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_STATUS_CHOICES,
        default='ACTIVE',
        help_text="Current employment status"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the employee is currently active"
    )
    
    class Meta:
        unique_together = [['organization', 'employee_code']]
        ordering = ['-created_at']
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
        indexes = [
            models.Index(fields=['organization', 'employee_code']),
            models.Index(fields=['organization', 'employment_status']),
        ]
    
    def __str__(self):
        """Return employee code and full name for admin readability."""
        full_name = f"{self.first_name} {self.middle_name} {self.last_name}".replace('  ', ' ').strip()
        return f"{self.employee_code} - {full_name}"
    
    def get_full_name(self):
        """Return the employee's full name."""
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        return ' '.join(parts)
