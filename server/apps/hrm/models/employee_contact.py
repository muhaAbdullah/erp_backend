from django.db import models
from coresite.mixin.basemodel import BaseModel
from .employee import Employee


class EmployeeContact(BaseModel):
    """
    Employee Contact Information model with multi-tenant isolation.
    
    Stores contact details and address information for employees.
    Inherits from BaseModel to ensure organization-level tenant isolation.
    
    Features:
    - Personal and official email addresses
    - Multiple phone numbers (primary and alternate)
    - Present and permanent addresses
    - Location information (city, state, country, postal code)
    """
    
    employee = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        related_name='contact_info',
        help_text="Employee this contact information belongs to"
    )
    personal_email = models.EmailField(
        blank=True,
        help_text="Personal email address"
    )
    official_email = models.EmailField(
        blank=True,
        help_text="Official/company email address"
    )
    mobile_number = models.CharField(
        max_length=20,
        help_text="Primary mobile/phone number"
    )
    alternate_mobile = models.CharField(
        max_length=20,
        blank=True,
        help_text="Alternate contact number"
    )
    present_address = models.TextField(
        blank=True,
        help_text="Current residential address"
    )
    permanent_address = models.TextField(
        blank=True,
        help_text="Permanent/home address"
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        help_text="City of residence"
    )
    state = models.CharField(
        max_length=100,
        blank=True,
        help_text="State/province of residence"
    )
    country = models.CharField(
        max_length=100,
        blank=True,
        help_text="Country of residence"
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        help_text="Postal/ZIP code"
    )
    
    class Meta:
        verbose_name = 'Employee Contact Information'
        verbose_name_plural = 'Employee Contact Information'
        indexes = [
            models.Index(fields=['organization', 'employee']),
            models.Index(fields=['organization', 'mobile_number']),
        ]
    
    def __str__(self):
        """Return employee code with contact info label for admin readability."""
        return f"Contact Info - {self.employee.employee_code}"
