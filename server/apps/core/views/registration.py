from datetime import date
from django.conf import settings
from rest_framework import status
from django.db import transaction
from rest_framework import permissions
from apps.core.models import (
    UserActivation,
    Organization,
    Role,
    Permission,
    RolePermission
)
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from utils.threads.email_thread import send_mail
from apps.core.serializers import CreateUserSerializer
from apps.userprofile.serializers import UserProfileSerializer
from apps.core.utils.reset_email_token_util import reset_email_token
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample, inline_serializer
from rest_framework import serializers as drf_serializers


User = get_user_model()
email = settings.EMAIL_HOST_USER
react_domain = settings.REACT_DOMAIN


def create_default_permissions():
    """
    Create default permissions if they don't exist.
    Returns list of all Permission objects.
    """
    default_permissions = [
        # User permissions
        {'name': 'Create User', 'permission_code': 'user.create', 'description': 'Can create new users'},
        {'name': 'Read User', 'permission_code': 'user.read', 'description': 'Can view users'},
        {'name': 'Update User', 'permission_code': 'user.update', 'description': 'Can update users'},
        {'name': 'Delete User', 'permission_code': 'user.delete', 'description': 'Can delete users'},
        
        # Role permissions
        {'name': 'Create Role', 'permission_code': 'role.create', 'description': 'Can create roles'},
        {'name': 'Read Role', 'permission_code': 'role.read', 'description': 'Can view roles'},
        {'name': 'Update Role', 'permission_code': 'role.update', 'description': 'Can update roles'},
        {'name': 'Delete Role', 'permission_code': 'role.delete', 'description': 'Can delete roles'},
        
        # Organization permissions
        {'name': 'Create Organization', 'permission_code': 'organization.create', 'description': 'Can create organizations'},
        {'name': 'Read Organization', 'permission_code': 'organization.read', 'description': 'Can view organizations'},
        {'name': 'Update Organization', 'permission_code': 'organization.update', 'description': 'Can update organizations'},
        {'name': 'Delete Organization', 'permission_code': 'organization.delete', 'description': 'Can delete organizations'},
        
        # Profile permissions
        {'name': 'Create Profile', 'permission_code': 'profile.create', 'description': 'Can create profiles'},
        {'name': 'Read Profile', 'permission_code': 'profile.read', 'description': 'Can view profiles'},
        {'name': 'Update Profile', 'permission_code': 'profile.update', 'description': 'Can update profiles'},
        {'name': 'Delete Profile', 'permission_code': 'profile.delete', 'description': 'Can delete profiles'},
    ]
    
    permissions = []
    for perm_data in default_permissions:
        perm, created = Permission.objects.get_or_create(
            permission_code=perm_data['permission_code'],
            defaults={
                'name': perm_data['name'],
                'description': perm_data['description']
            }
        )
        permissions.append(perm)
    
    return permissions


class RegistrationView(APIView):
    permission_classes = (permissions.AllowAny,)

    @extend_schema(
        tags=['Auth'],
        summary='Public registration (DISABLED)',
        description=(
            'Public registration is disabled. '
            'Please contact your system administrator to create an account. '
            'Admins can create users via POST /api/user/create-user/ or POST /api/user/users/'
        ),
        request=inline_serializer(
            name='RegisterRequest',
            fields={
                'email': drf_serializers.EmailField(required=False, help_text='Not used - registration disabled'),
                'username': drf_serializers.CharField(required=False, help_text='Not used - registration disabled'),
                'password': drf_serializers.CharField(required=False, help_text='Not used - registration disabled', write_only=True),
            },
        ),
        responses={
            403: OpenApiResponse(
                description='Public registration is disabled',
                response=inline_serializer(
                    name='RegisterDisabled',
                    fields={
                        'error': drf_serializers.CharField(help_text='Error message'),
                        'message': drf_serializers.CharField(help_text='Instruction message'),
                    },
                ),
            ),
        },
        examples=[
            OpenApiExample(
                name='Registration attempt',
                value={
                    'error': 'Public registration is disabled',
                    'message': 'Please contact your system administrator to create an account'
                },
                response_only=True,
                status_codes=['403'],
            ),
        ]
    )
    def post(self, request, *args, **kwargs):
        return Response(
            {
                "error": "Public registration is disabled",
                "message": "Please contact your system administrator to create an account"
            },
            status=status.HTTP_403_FORBIDDEN
        )
