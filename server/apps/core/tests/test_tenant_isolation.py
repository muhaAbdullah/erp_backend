"""
Simple test cases for tenant isolation and RBAC enforcement.

These tests verify:
- Users can only access data from their own organization
- Role assignment is validated against organization
- Super admins can access all data
- Permission checks work correctly
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.core.models import Organization, Role, Permission, RolePermission
from apps.core.utils.permission_helper import has_permission, set_current_user
from apps.core.validators import (
    validate_role_organization,
    validate_organization_access,
    validate_same_organization
)
from rest_framework.exceptions import ValidationError, PermissionDenied

User = get_user_model()


class TenantIsolationTestCase(TestCase):
    """Test cases for tenant isolation."""
    
    def setUp(self):
        """Set up test data."""
        # Create two organizations
        self.org1 = Organization.objects.create(name='Organization 1')
        self.org2 = Organization.objects.create(name='Organization 2')
        
        # Create roles for each organization
        self.role_org1 = Role.objects.create(
            name='Admin',
            organization=self.org1
        )
        self.role_org2 = Role.objects.create(
            name='Admin',
            organization=self.org2
        )
        
        # Create users in different organizations
        self.user_org1 = User.objects.create_user(
            email='user1@org1.com',
            username='user1',
            password='password123',
            organization=self.org1,
            role=self.role_org1
        )
        self.user_org1.is_active = True
        self.user_org1.save()
        
        self.user_org2 = User.objects.create_user(
            email='user2@org2.com',
            username='user2',
            password='password123',
            organization=self.org2,
            role=self.role_org2
        )
        self.user_org2.is_active = True
        self.user_org2.save()
        
        # Create super admin
        self.super_admin = User.objects.create_superuser(
            email='admin@system.com',
            username='superadmin',
            password='password123'
        )
    
    def test_role_must_belong_to_user_organization(self):
        """Test that role must belong to user's organization."""
        # Try to assign org2's role to org1's user
        with self.assertRaises(ValidationError):
            validate_role_organization(self.user_org1, self.role_org2)
    
    def test_role_validation_passes_for_same_organization(self):
        """Test that role validation passes for same organization."""
        # This should not raise an error
        result = validate_role_organization(self.user_org1, self.role_org1)
        self.assertTrue(result)
    
    def test_super_admin_can_assign_any_role(self):
        """Test that super admin can assign roles across organizations."""
        # Super admin should be able to assign any role
        result = validate_role_organization(self.super_admin, self.role_org1)
        self.assertTrue(result)
        
        result = validate_role_organization(self.super_admin, self.role_org2)
        self.assertTrue(result)
    
    def test_user_cannot_access_other_organization(self):
        """Test that users cannot access other organizations."""
        with self.assertRaises(PermissionDenied):
            validate_organization_access(self.user_org1, self.org2)
    
    def test_user_can_access_own_organization(self):
        """Test that users can access their own organization."""
        result = validate_organization_access(self.user_org1, self.org1)
        self.assertTrue(result)
    
    def test_super_admin_can_access_all_organizations(self):
        """Test that super admin can access all organizations."""
        result = validate_organization_access(self.super_admin, self.org1)
        self.assertTrue(result)
        
        result = validate_organization_access(self.super_admin, self.org2)
        self.assertTrue(result)
    
    def test_tenant_manager_filters_by_organization(self):
        """Test that TenantManager filters data by organization."""
        # Set current user to org1 user
        set_current_user(self.user_org1)
        
        # Query should only return org1's roles
        roles = Role.objects.all()
        org1_roles = roles.filter(organization=self.org1)
        # Should see only roles from org1
        self.assertTrue(all(r.organization == self.org1 for r in roles))
        self.assertTrue(org1_roles.exists())
        
        # Set current user to org2 user
        set_current_user(self.user_org2)
        
        # Query should only return org2's roles
        roles = Role.objects.all()
        org2_roles = roles.filter(organization=self.org2)
        # Should see only roles from org2
        self.assertTrue(all(r.organization == self.org2 for r in roles))
        self.assertTrue(org2_roles.exists())
        
        # Clean up
        set_current_user(None)
    
    def test_super_admin_sees_all_data(self):
        """Test that super admin sees all data."""
        # Set current user to super admin
        set_current_user(self.super_admin)
        
        # Query should return roles from all organizations
        roles = Role.objects.all()
        # Should see roles from both organizations
        self.assertTrue(roles.filter(organization=self.org1).exists())
        self.assertTrue(roles.filter(organization=self.org2).exists())
        
        # Clean up
        set_current_user(None)
    
    def test_user_without_organization_sees_nothing(self):
        """Test that users without organization see no data."""
        # Create user without organization
        user_no_org = User.objects.create_user(
            email='noorg@test.com',
            username='noorg',
            password='password123'
        )
        user_no_org.is_active = True
        user_no_org.save()
        
        # Set current user
        set_current_user(user_no_org)
        
        # Query should return empty queryset (no access to any organization's data)
        roles = Role.objects.all()
        # Shouldn't see any of our test organizations' roles
        self.assertFalse(roles.filter(organization=self.org1).exists())
        self.assertFalse(roles.filter(organization=self.org2).exists())
        
        # Clean up
        set_current_user(None)


class RBACTestCase(TestCase):
    """Test cases for RBAC (Role-Based Access Control)."""
    
    def setUp(self):
        """Set up test data."""
        # Create organization
        self.org = Organization.objects.create(name='Test Organization RBAC')
        
        # Get or create permissions (may exist from migrations)
        self.perm_read, _ = Permission.objects.get_or_create(
            permission_code='user.read',
            defaults={'name': 'Read Users'}
        )
        self.perm_create, _ = Permission.objects.get_or_create(
            permission_code='user.create',
            defaults={'name': 'Create Users'}
        )
        
        # Create role with permissions
        self.admin_role = Role.objects.create(
            name='Admin',
            organization=self.org
        )
        RolePermission.objects.create(
            role=self.admin_role,
            permission=self.perm_read
        )
        RolePermission.objects.create(
            role=self.admin_role,
            permission=self.perm_create
        )
        
        # Create role without permissions
        self.viewer_role = Role.objects.create(
            name='Viewer',
            organization=self.org
        )
        RolePermission.objects.create(
            role=self.viewer_role,
            permission=self.perm_read
        )
        
        # Create users
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            username='admin',
            password='password123',
            organization=self.org,
            role=self.admin_role
        )
        self.admin_user.is_active = True
        self.admin_user.save()
        
        self.viewer_user = User.objects.create_user(
            email='viewer@test.com',
            username='viewer',
            password='password123',
            organization=self.org,
            role=self.viewer_role
        )
        self.viewer_user.is_active = True
        self.viewer_user.save()
        
        self.user_no_role = User.objects.create_user(
            email='norole@test.com',
            username='norole',
            password='password123',
            organization=self.org
        )
        self.user_no_role.is_active = True
        self.user_no_role.save()
    
    def test_user_with_permission_has_access(self):
        """Test that user with permission has access."""
        self.assertTrue(has_permission(self.admin_user, 'user.read'))
        self.assertTrue(has_permission(self.admin_user, 'user.create'))
    
    def test_user_without_permission_denied(self):
        """Test that user without permission is denied."""
        self.assertTrue(has_permission(self.viewer_user, 'user.read'))
        self.assertFalse(has_permission(self.viewer_user, 'user.create'))
    
    def test_user_without_role_has_no_permissions(self):
        """Test that user without role has no permissions."""
        self.assertFalse(has_permission(self.user_no_role, 'user.read'))
        self.assertFalse(has_permission(self.user_no_role, 'user.create'))
    
    def test_super_admin_has_all_permissions(self):
        """Test that super admin has all permissions."""
        super_admin = User.objects.create_superuser(
            email='superadmin@test.com',
            username='superadmin',
            password='password123'
        )
        
        self.assertTrue(has_permission(super_admin, 'user.read'))
        self.assertTrue(has_permission(super_admin, 'user.create'))
        self.assertTrue(has_permission(super_admin, 'any.permission'))


class ValidationTestCase(TestCase):
    """Test cases for security validators."""
    
    def setUp(self):
        """Set up test data."""
        self.org1 = Organization.objects.create(name='Organization 1')
        self.org2 = Organization.objects.create(name='Organization 2')
        
        self.role_org1 = Role.objects.create(
            name='Test Role',
            organization=self.org1
        )
        
        self.user = User.objects.create_user(
            email='user@test.com',
            username='user',
            password='password123',
            organization=self.org1
        )
        self.user.is_active = True
        self.user.save()
    
    def test_validate_same_organization_with_matching_org(self):
        """Test validation passes for same organization."""
        result = validate_same_organization(self.user, self.role_org1)
        self.assertTrue(result)
    
    def test_validate_same_organization_with_different_org(self):
        """Test validation fails for different organization."""
        role_org2 = Role.objects.create(
            name='Test Role 2',
            organization=self.org2
        )
        
        with self.assertRaises(PermissionDenied):
            validate_same_organization(self.user, role_org2)
    
    def test_user_model_save_validates_role_organization(self):
        """Test that User.save() validates role-organization relationship."""
        # Create user with org1
        user = User(
            email='test@test.com',
            username='testuser',
            organization=self.org1,
            role=self.role_org1  # Same org - should work
        )
        user.set_password('password123')
        user.save()  # Should not raise error
        
        # Try to assign role from different org
        role_org2 = Role.objects.create(
            name='Role Org 2',
            organization=self.org2
        )
        
        user.role = role_org2
        with self.assertRaises(Exception):  # Should raise ValidationError
            user.save()
