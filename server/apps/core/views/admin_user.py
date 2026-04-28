from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from apps.core.models import User, Organization, Role
from apps.core.serializers import CreateUserSerializer, UserDetailSerializer
from apps.core.permissions import IsSuperAdmin, IsOrganizationAdmin
from apps.core.utils.permission_helper import has_permission
from apps.core.utils.audit_logger import log_action, get_model_changes
from apps.userprofile.models import UserProfile
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from rest_framework import serializers as drf_serializers


class AdminUserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for admin user management.
    Super Admin: Full access to all users
    Org Admin: Access to users in their organization only
    
    Endpoints:
    - POST /api/user/users/ - Create regular user
    - POST /api/user/users/create_super_admin/ - Create super admin (super admin only)
    - GET /api/user/users/ - List users
    - GET /api/user/users/{id}/ - Get user details
    - PATCH /api/user/users/{id}/ - Update user
    - DELETE /api/user/users/{id}/ - Delete user
    """
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Return queryset based on user role.
        Super admin sees all users, org admin sees only their organization's users.
        """
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return User.objects.none()
        
        if self.request.user.is_super_admin:
            return User.objects.all()
        return User.objects.filter(organization=self.request.user.organization)
    
    @extend_schema(
        tags=['User Management'],
        summary="Create User (Admin Only)",
        description="Create a new user. Super admin must provide organization_id, org admin creates in their own organization.",
        request=inline_serializer(
            name='AdminCreateUserRequest',
            fields={
                'email': drf_serializers.EmailField(required=True, help_text='User email address'),
                'username': drf_serializers.CharField(required=True, help_text='Unique username'),
                'password': drf_serializers.CharField(required=True, help_text='User password', write_only=True),
                'organization_id': drf_serializers.IntegerField(
                    required=False,
                    help_text='Organization ID (required for super admin, ignored for org admin)'
                ),
                'role_id': drf_serializers.IntegerField(
                    required=False,
                    help_text='Role ID (must belong to same organization)'
                ),
                'profile': inline_serializer(
                    name='AdminCreateUserProfileRequest',
                    fields={
                        'first_name': drf_serializers.CharField(required=False, help_text='User first name'),
                        'last_name': drf_serializers.CharField(required=False, help_text='User last name'),
                    },
                    required=False,
                    help_text='Optional user profile information'
                ),
            },
        ),
        responses={
            201: OpenApiResponse(
                description='User created successfully',
                response=inline_serializer(
                    name='AdminCreateUserSuccess',
                    fields={
                        'message': drf_serializers.CharField(),
                        'user_id': drf_serializers.IntegerField(),
                        'email': drf_serializers.EmailField(),
                    },
                ),
            ),
            400: OpenApiResponse(description='Validation error'),
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='Organization or Role not found'),
        },
    )
    def create(self, request):
        """Create a new user (admin only)."""
        # Check permission
        if not request.user.is_super_admin:
            if not has_permission(request.user, 'user.create'):
                return Response(
                    {"error": "Permission denied"},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Get organization
        if request.user.is_super_admin:
            org_id = request.data.get('organization_id')
            if not org_id:
                return Response(
                    {"organization_id": "Required for super admin"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            try:
                organization = Organization.objects.get(id=org_id)
            except Organization.DoesNotExist:
                return Response(
                    {"organization_id": "Organization not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            organization = request.user.organization
        
        # Get role if provided
        role = None
        role_id = request.data.get('role_id')
        if role_id:
            try:
                role = Role.objects.get(id=role_id)
                if role.organization != organization:
                    return Response(
                        {"role_id": "Role must belong to same organization"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except Role.DoesNotExist:
                return Response(
                    {"role_id": "Role not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Create user
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                user = User.objects.create_user(
                    email=serializer.validated_data['email'],
                    username=serializer.validated_data['username'],
                    password=serializer.validated_data['password'],
                    organization=organization,
                    role=role
                )
                
                # Create profile if data provided
                profile_data = request.data.get('profile', {})
                if profile_data:
                    UserProfile.objects.create(
                        user=user,
                        first_name=profile_data.get('first_name', ''),
                        last_name=profile_data.get('last_name', '')
                    )
                
                # Log user creation
                log_action(
                    user=request.user,
                    action='CREATE',
                    model_name='User',
                    object_id=user.id,
                    changes=get_model_changes(None, user, ['email', 'username', 'organization', 'role']),
                    request=request
                )
                
                return Response(
                    {
                        "message": "User created successfully",
                        "user_id": user.id,
                        "email": user.email
                    },
                    status=status.HTTP_201_CREATED
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        tags=['User Management'],
        summary="List Users",
        description="List all users. Super admin sees all users, org admin sees only their organization's users.",
        responses={
            200: UserDetailSerializer(many=True),
            403: OpenApiResponse(description='Permission denied'),
        },
    )
    def list(self, request):
        """List users based on permission."""
        if not request.user.is_super_admin:
            if not has_permission(request.user, 'user.read'):
                return Response(
                    {"error": "Permission denied"},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        tags=['User Management'],
        summary="Get User Details",
        description="Retrieve details of a specific user.",
        responses={
            200: UserDetailSerializer,
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='User not found'),
        },
    )
    def retrieve(self, request, pk=None):
        """Retrieve a specific user."""
        if not request.user.is_super_admin:
            if not has_permission(request.user, 'user.read'):
                return Response(
                    {"error": "Permission denied"},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        try:
            user = self.get_queryset().get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(user)
        return Response(serializer.data)
    
    @extend_schema(
        tags=['User Management'],
        summary="Update User",
        description="Update user information. Cannot change organization.",
        request=UserDetailSerializer,
        responses={
            200: UserDetailSerializer,
            400: OpenApiResponse(description='Validation error'),
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='User not found'),
        },
    )
    def update(self, request, pk=None):
        """Update a user (full update)."""
        if not request.user.is_super_admin:
            if not has_permission(request.user, 'user.update'):
                return Response(
                    {"error": "Permission denied"},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        try:
            user = self.get_queryset().get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Store old values before update
        old_email = user.email
        old_organization = user.organization
        old_role = user.role
        old_is_active = user.is_active
        
        serializer = self.get_serializer(user, data=request.data)
        if serializer.is_valid():
            updated_user = serializer.save()
            
            # Log the update
            log_action(
                user=request.user,
                action='UPDATE',
                model_name='User',
                object_id=updated_user.id,
                changes={
                    'before': {
                        'email': old_email,
                        'organization': str(old_organization) if old_organization else None,
                        'role': str(old_role) if old_role else None,
                        'is_active': old_is_active
                    },
                    'after': {
                        'email': updated_user.email,
                        'organization': str(updated_user.organization) if updated_user.organization else None,
                        'role': str(updated_user.role) if updated_user.role else None,
                        'is_active': updated_user.is_active
                    }
                },
                request=request
            )
            
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        tags=['User Management'],
        summary="Partial Update User",
        description="Partially update user information. Cannot change organization.",
        request=UserDetailSerializer,
        responses={
            200: UserDetailSerializer,
            400: OpenApiResponse(description='Validation error'),
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='User not found'),
        },
    )
    def partial_update(self, request, pk=None):
        """Partially update a user."""
        if not request.user.is_super_admin:
            if not has_permission(request.user, 'user.update'):
                return Response(
                    {"error": "Permission denied"},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        try:
            user = self.get_queryset().get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Store old values before update
        old_email = user.email
        old_organization = user.organization
        old_role = user.role
        old_is_active = user.is_active
        
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            updated_user = serializer.save()
            
            # Log the update
            log_action(
                user=request.user,
                action='UPDATE',
                model_name='User',
                object_id=updated_user.id,
                changes={
                    'before': {
                        'email': old_email,
                        'organization': str(old_organization) if old_organization else None,
                        'role': str(old_role) if old_role else None,
                        'is_active': old_is_active
                    },
                    'after': {
                        'email': updated_user.email,
                        'organization': str(updated_user.organization) if updated_user.organization else None,
                        'role': str(updated_user.role) if updated_user.role else None,
                        'is_active': updated_user.is_active
                    }
                },
                request=request
            )
            
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        tags=['User Management'],
        summary="Delete User",
        description="Delete a user from the system.",
        responses={
            204: OpenApiResponse(description='User deleted successfully'),
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='User not found'),
        },
    )
    def destroy(self, request, pk=None):
        """Delete a user."""
        if not request.user.is_super_admin:
            if not has_permission(request.user, 'user.delete'):
                return Response(
                    {"error": "Permission denied"},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        try:
            user = self.get_queryset().get(pk=pk)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Store user info before deletion
        user_id = user.id
        user_email = user.email
        user_username = user.username
        
        user.delete()
        
        # Log the deletion
        log_action(
            user=request.user,
            action='DELETE',
            model_name='User',
            object_id=user_id,
            changes={'before': {'email': user_email, 'username': user_username}, 'after': {}},
            request=request
        )
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @extend_schema(
        tags=['User Management'],
        summary="Create Super Admin",
        description="Create a new super admin user. Only existing super admins can use this endpoint.",
        request=inline_serializer(
            name='CreateSuperAdminRequest',
            fields={
                'email': drf_serializers.EmailField(required=True, help_text='Super admin email address'),
                'username': drf_serializers.CharField(required=True, help_text='Unique username'),
                'password': drf_serializers.CharField(required=True, help_text='Super admin password', write_only=True),
            },
        ),
        responses={
            201: OpenApiResponse(
                description='Super admin created successfully',
                response=inline_serializer(
                    name='CreateSuperAdminSuccess',
                    fields={
                        'message': drf_serializers.CharField(),
                        'user_id': drf_serializers.IntegerField(),
                        'email': drf_serializers.EmailField(),
                        'username': drf_serializers.CharField(),
                    },
                ),
            ),
            400: OpenApiResponse(description='Validation error'),
            403: OpenApiResponse(description='Only super admins can create super admins'),
        },
    )
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, IsSuperAdmin])
    def create_super_admin(self, request):
        """
        Create a new super admin user.
        Only existing super admins can access this endpoint.
        """
        # Validate required fields
        email = request.data.get('email')
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not all([email, username, password]):
            return Response(
                {"error": "email, username, and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return Response(
                {"email": "User with this email already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if User.objects.filter(username=username).exists():
            return Response(
                {"username": "User with this username already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create super admin
        user = User.objects.create_user(
            email=email,
            username=username,
            password=password,
            organization=None,  # Super admins don't need organization
            role=None  # Super admins don't need role
        )
        
        # Set super admin fields after creation
        user.is_super_admin = True
        user.is_active = True
        user.is_staff = True  # For Django admin access
        user.is_superuser = True  # For Django admin full access
        user.save()
        
        # Log super admin creation
        log_action(
            user=request.user,
            action='CREATE',
            model_name='User',
            object_id=user.id,
            changes=get_model_changes(None, user, ['email', 'username', 'is_super_admin']),
            request=request
        )
        
        return Response(
            {
                "message": "Super admin created successfully",
                "user_id": user.id,
                "email": user.email,
                "username": user.username
            },
            status=status.HTTP_201_CREATED
        )
