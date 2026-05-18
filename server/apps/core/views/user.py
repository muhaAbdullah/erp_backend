"""
User detail view with RBAC enforcement.
"""
from rest_framework import permissions
from rest_framework import generics
from django.contrib.auth import get_user_model
from apps.core.serializers import UserDetailSerializer
from apps.core.permissions import IsOwnerOrHasPermission
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse, inline_serializer
from rest_framework import serializers as drf_serializers

User = get_user_model()


@extend_schema_view(
    get=extend_schema(
        tags=['User'],
        summary='Get current user',
        description=(
            'Returns the complete profile details of the currently authenticated user, '
            'including organization, role, permissions, and profile information.'
        ),
        responses={
            200: OpenApiResponse(
                description='Current user details',
                response=inline_serializer(
                    name='UserDetailResponse',
                    fields={
                        'id': drf_serializers.IntegerField(help_text='User ID'),
                        'username': drf_serializers.CharField(help_text='Username'),
                        'email': drf_serializers.EmailField(help_text='Email address'),
                        'user_type': drf_serializers.CharField(help_text='User type (e.g., user, admin)'),
                        'is_active': drf_serializers.BooleanField(help_text='Account active status'),
                        'is_super_admin': drf_serializers.BooleanField(help_text='Super admin status'),
                        'organization': drf_serializers.IntegerField(help_text='Organization ID'),
                        'organization_name': drf_serializers.CharField(help_text='Organization name'),
                        'role': drf_serializers.IntegerField(help_text='Role ID'),
                        'role_name': drf_serializers.CharField(help_text='Role name'),
                        'permissions': drf_serializers.ListField(
                            child=drf_serializers.CharField(),
                            help_text='List of permission codes'
                        ),
                        'profile': inline_serializer(
                            name='ProfileResponse',
                            fields={
                                'id': drf_serializers.IntegerField(help_text='Profile ID'),
                                'first_name': drf_serializers.CharField(help_text='First name'),
                                'last_name': drf_serializers.CharField(help_text='Last name'),
                                'image': drf_serializers.URLField(allow_null=True, help_text='Profile image URL'),
                            }
                        ),
                        'created_at': drf_serializers.DateTimeField(help_text='Account creation timestamp'),
                        'updated_at': drf_serializers.DateTimeField(help_text='Last update timestamp'),
                    }
                )
            ),
            401: OpenApiResponse(description='Authentication credentials not provided or invalid.'),
        }
    ),
    put=extend_schema(
        tags=['User'],
        summary='Update current user',
        description=(
            'Fully updates the profile of the currently authenticated user. '
            'You can update user fields and nested profile information. '
            'Organization and role can be updated if permitted.'
        ),
        request=inline_serializer(
            name='UserUpdateRequest',
            fields={
                'username': drf_serializers.CharField(required=False, help_text='Username'),
                'email': drf_serializers.EmailField(required=False, help_text='Email address'),
                'user_type': drf_serializers.CharField(required=False, help_text='User type'),
                'is_active': drf_serializers.BooleanField(required=False, help_text='Account active status'),
                'organization': drf_serializers.IntegerField(required=False, help_text='Organization ID'),
                'role': drf_serializers.IntegerField(required=False, help_text='Role ID'),
                'profile': inline_serializer(
                    name='ProfileUpdateRequest',
                    fields={
                        'first_name': drf_serializers.CharField(required=False, help_text='First name'),
                        'last_name': drf_serializers.CharField(required=False, help_text='Last name'),
                        'image': drf_serializers.ImageField(required=False, help_text='Profile image'),
                    },
                    required=False
                ),
            }
        ),
        responses={
            200: OpenApiResponse(description='User updated successfully'),
            400: OpenApiResponse(description='Validation error.'),
            401: OpenApiResponse(description='Authentication credentials not provided or invalid.'),
        }
    ),
    patch=extend_schema(
        tags=['User'],
        summary='Partial update current user',
        description=(
            'Partially updates the profile of the currently authenticated user. '
            'Only the fields provided will be updated. Others remain unchanged.'
        ),
        request=inline_serializer(
            name='UserPartialUpdateRequest',
            fields={
                'username': drf_serializers.CharField(required=False, help_text='Username'),
                'email': drf_serializers.EmailField(required=False, help_text='Email address'),
                'user_type': drf_serializers.CharField(required=False, help_text='User type'),
                'is_active': drf_serializers.BooleanField(required=False, help_text='Account active status'),
                'organization': drf_serializers.IntegerField(required=False, help_text='Organization ID'),
                'role': drf_serializers.IntegerField(required=False, help_text='Role ID'),
                'profile': inline_serializer(
                    name='ProfilePartialUpdateRequest',
                    fields={
                        'first_name': drf_serializers.CharField(required=False, help_text='First name'),
                        'last_name': drf_serializers.CharField(required=False, help_text='Last name'),
                        'image': drf_serializers.ImageField(required=False, help_text='Profile image'),
                    },
                    required=False
                ),
            }
        ),
        responses={
            200: OpenApiResponse(description='User updated successfully'),
            400: OpenApiResponse(description='Validation error.'),
            401: OpenApiResponse(description='Authentication credentials not provided or invalid.'),
        }
    ),
    delete=extend_schema(
        tags=['User'],
        summary='Delete current user',
        description='Deletes the account of the currently authenticated user. This action is irreversible.',
        responses={
            204: OpenApiResponse(description='User deleted successfully'),
            401: OpenApiResponse(description='Authentication credentials not provided or invalid.'),
        }
    ),
)
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    User detail view that allows users to manage their own profile.
    
    Uses IsOwnerOrHasPermission to allow:
    - Users to access/update their own profile without special permissions
    - Admin users with user.read permission to view other users
    - Admin users with user.update permission to update other users
    """
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrHasPermission)
    permission_code = 'user.read'  # Required for accessing other users

    def get_object(self):
        """Always return the current user for this endpoint."""
        return self.request.user
