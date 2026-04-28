"""
User profile viewset with RBAC and tenant isolation.
"""
from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import UserProfile
from utils.paginations.pagination import LimitOffsetPagination
from django_filters import rest_framework as backend_filters
from .filters import UserProfileFilter
from .serializers import UserProfileSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


@extend_schema_view(
    list=extend_schema(
        tags=['User Profile'],
        summary='List user profiles',
        description=(
            'Returns a paginated list of all active user profiles. '
            'Supports filtering by user, user_type, is_active, is_staff, is_superuser, and email. '
            'Supports full-text search on first_name, last_name, and username.'
        ),
        parameters=[
            OpenApiParameter('limit', OpenApiTypes.INT, OpenApiParameter.QUERY, description='Number of results to return (default 100, max 100).'),
            OpenApiParameter('offset', OpenApiTypes.INT, OpenApiParameter.QUERY, description='Starting position in the result set.'),
            OpenApiParameter('search', OpenApiTypes.STR, OpenApiParameter.QUERY, description='Search by first_name, last_name, or username.'),
            OpenApiParameter('user', OpenApiTypes.INT, OpenApiParameter.QUERY, description='Filter by user ID.'),
            OpenApiParameter('user__user_type', OpenApiTypes.STR, OpenApiParameter.QUERY, description='Filter by user type: user, admin, super_admin.'),
            OpenApiParameter('user__is_active', OpenApiTypes.BOOL, OpenApiParameter.QUERY, description='Filter by account active status.'),
            OpenApiParameter('user__email', OpenApiTypes.STR, OpenApiParameter.QUERY, description='Filter by exact email address.'),
        ],
    ),
    retrieve=extend_schema(
        tags=['User Profile'],
        summary='Retrieve a user profile',
        description='Returns the profile for the given username.',
        parameters=[
            OpenApiParameter('username', OpenApiTypes.STR, OpenApiParameter.PATH, description='Username of the user whose profile to retrieve.'),
        ],
    ),
    create=extend_schema(
        tags=['User Profile'],
        summary='Create a user profile',
        description='Creates a new profile for the authenticated user.',
    ),
    update=extend_schema(
        tags=['User Profile'],
        summary='Update a user profile',
        description='Fully updates the profile for the given username. Requires authentication.',
        parameters=[
            OpenApiParameter('username', OpenApiTypes.STR, OpenApiParameter.PATH, description='Username of the user whose profile to update.'),
        ],
    ),
    partial_update=extend_schema(
        tags=['User Profile'],
        summary='Partial update a user profile',
        description='Partially updates the profile for the given username. Requires authentication.',
        parameters=[
            OpenApiParameter('username', OpenApiTypes.STR, OpenApiParameter.PATH, description='Username of the user whose profile to partially update.'),
        ],
    ),
    destroy=extend_schema(
        tags=['User Profile'],
        summary='Delete a user profile',
        description='Deletes the profile for the given username. Requires authentication.',
        parameters=[
            OpenApiParameter('username', OpenApiTypes.STR, OpenApiParameter.PATH, description='Username of the user whose profile to delete.'),
        ],
    ),
)
class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user profiles with simplified access control.
    
    Regular users can only view/update their own profile.
    Super admins can access all profiles.
    """
    pagination_class = LimitOffsetPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [
        backend_filters.DjangoFilterBackend,
        filters.SearchFilter,
    ]
    filterset_class = UserProfileFilter
    search_fields = ['first_name', 'last_name', 'user__username', 'user__email']
    serializer_class = UserProfileSerializer
    lookup_field = 'user__username'
    lookup_url_kwarg = 'username'

    def get_queryset(self):
        """
        Filter queryset based on user type.
        Super admins see all profiles, regular users see only their own.
        """
        # Super admin sees all profiles
        if self.request.user.is_super_admin:
            return UserProfile.objects.all()
        
        # Regular users see only their own profile
        return UserProfile.objects.filter(user=self.request.user)
    
    def list(self, request, *args, **kwargs):
        """
        For normal users, return their profile directly (not a list).
        For super admins, return the full list.
        """
        # Normal users get their own profile, not a list
        if not request.user.is_super_admin:
            try:
                profile = UserProfile.objects.get(user=request.user)
                serializer = self.get_serializer(profile)
                return Response(serializer.data)
            except UserProfile.DoesNotExist:
                return Response(
                    {"detail": "Profile not found. Please create one."},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Super admin gets full list
        return super().list(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """
        Always assign profile to the logged-in user.
        """
        serializer.save(user=self.request.user)
