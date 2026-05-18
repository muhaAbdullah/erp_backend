from django.db import models
from coresite.mixin.basemodel import BaseModel
from .employee import Employee


class EmployeeGovernment(BaseModel):
    """
    Employee Government Information model with multi-tenant isolation.
    
    Stores government-issued IDs and banking information for employees.
    Inherits from BaseModel to ensure organization-level tenant isolation.
    
    Features:
    - National identification documents (NIC/CNIC, passport)
    - Tax and social security information (NTN, EOBI)
    - Banking details for salary processing
    
    Security Note: This model contains sensitive information and should be
    protected with appropriate access controls and encryption in production.
    """
    
    employee = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        related_name='government_info',
        help_text="Employee this government information belongs to"
    )
    national_id = models.CharField(
        max_length=50,
        blank=True,
        help_text="National ID number (CNIC/NIC)"
    )
    passport_number = models.CharField(
        max_length=50,
        blank=True,
        help_text="Passport number"
    )
    tax_identification = models.CharField(
        max_length=50,
        blank=True,
        help_text="Tax identification number (NTN)"
    )
    social_security = models.CharField(
        max_length=50,
        blank=True,
        help_text="Social security number (EOBI)"
    )
    bank_account_number = models.CharField(
        max_length=50,
        blank=True,
        help_text="Bank account number for salary deposits"
    )
    bank_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Name of the bank"
    )
    bank_branch = models.CharField(
        max_length=100,
        blank=True,
        help_text="Bank branch location"
    )
    
    class Meta:
        verbose_name = 'Employee Government Information'
        verbose_name_plural = 'Employee Government Information'
        indexes = [
            models.Index(fields=['organization', 'employee']),
            models.Index(fields=['organization', 'national_id']),
        ]
    
    def __str__(self):
        """Return employee code with government info label for admin readability."""
        return f"Government Info - {self.employee.employee_code}"
