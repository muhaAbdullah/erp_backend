# Generated migration for HRM permissions

from django.db import migrations


def create_hrm_permissions(apps, schema_editor):
    """
    Create HRM-specific permissions in the Permission model.
    """
    Permission = apps.get_model('core', 'Permission')
    
    # Define HRM permissions
    hrm_permissions = [
        # Employee permissions
        {
            'name': 'View Employee',
            'permission_code': 'view_employee',
            'description': 'Can view employee records'
        },
        {
            'name': 'Create Employee',
            'permission_code': 'create_employee',
            'description': 'Can create new employee records'
        },
        {
            'name': 'Update Employee',
            'permission_code': 'update_employee',
            'description': 'Can update employee records'
        },
        {
            'name': 'Delete Employee',
            'permission_code': 'delete_employee',
            'description': 'Can delete employee records'
        },
        
        # HRM Master Data permissions
        {
            'name': 'Manage HRM Masters',
            'permission_code': 'manage_hrm_masters',
            'description': 'Can manage HRM master data (departments, designations, shifts, etc.)'
        },
    ]
    
    # Create permissions
    for perm_data in hrm_permissions:
        Permission.objects.get_or_create(
            permission_code=perm_data['permission_code'],
            defaults={
                'name': perm_data['name'],
                'description': perm_data['description']
            }
        )


def reverse_hrm_permissions(apps, schema_editor):
    """
    Remove HRM permissions.
    """
    Permission = apps.get_model('core', 'Permission')
    
    hrm_permission_codes = [
        'view_employee',
        'create_employee',
        'update_employee',
        'delete_employee',
        'manage_hrm_masters',
    ]
    
    # Delete HRM permissions
    Permission.objects.filter(permission_code__in=hrm_permission_codes).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('hrm', '0001_initial'),
        ('core', '0004_rbac_data_setup'),
    ]

    operations = [
        migrations.RunPython(create_hrm_permissions, reverse_hrm_permissions),
    ]
