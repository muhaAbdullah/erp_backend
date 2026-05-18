from django.db import models
from coresite.mixin import AbstractTimeStampModel
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
)


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, organization=None, role=None, user_type='user'):
        """
        Creates and saves a User with the given email, username,
        password, organization, and role.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            user_type=user_type,
        )
        
        # Set organization and role if provided
        if organization:
            user.organization = organization
        if role:
            user.role = role
            
        user.is_staff = True
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username=None, password=None, organization=None, role=None, user_type='super_admin'):
        """
        Creates and saves a superuser with the given email, username,
        password, organization, and role.
        """
        user = self.create_user(
            email,
            password=password,
            username=username,
            organization=organization,
            role=role,
            user_type=user_type,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.user_type = 'super_admin'
        user.is_super_admin = True
        user.save(using=self._db)
        return user


USER_TYPE_CHOICES = (
    ('user', 'User'),
    ('admin', 'Admin'),
    ('super_admin', 'Super Admin'),

)


class User(AbstractBaseUser, AbstractTimeStampModel):
    """
    Custom user model with multi-tenancy and RBAC support.
    
    Features:
    - Multi-tenancy through organization field
    - Role-Based Access Control (RBAC) through role field
    - Super admin capability for cross-tenant access
    - Automatic role-organization validation
    
    Security:
    - Role must belong to same organization as user
    - Super admins bypass all permission checks
    - Regular users are restricted to their organization's data
    """
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    user_type = models.CharField(
        max_length=255, default='user', choices=USER_TYPE_CHOICES)
    username = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    
    # Multi-tenancy and RBAC fields
    organization = models.ForeignKey(
        'Organization',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        help_text="Organization this user belongs to"
    )
    role = models.ForeignKey(
        'Role',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        help_text="Role assigned to this user"
    )
    is_super_admin = models.BooleanField(
        default=False,
        help_text="Super admin has access to all organizations and bypasses all permission checks"
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password', 'username']

    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        """
        Override save to validate role-organization relationship.
        Ensures role belongs to same organization as user.
        """
        # Validate role belongs to user's organization (except for super admins)
        if self.role and self.organization and not self.is_super_admin:
            if self.role.organization != self.organization:
                from django.core.exceptions import ValidationError
                raise ValidationError(
                    f"Role '{self.role.name}' belongs to '{self.role.organization.name}' "
                    f"but user belongs to '{self.organization.name}'"
                )
        
        super().save(*args, **kwargs)

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Super admins have all permissions
        if self.is_super_admin:
            return True
        # Admin users have all permissions
        if self.is_admin:
            return True
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Super admins and admins have all module permissions
        if self.is_super_admin or self.is_admin:
            return True
        return True
