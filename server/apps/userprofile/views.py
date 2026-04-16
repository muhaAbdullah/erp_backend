from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny
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
    pagination_class = LimitOffsetPagination
    filter_backends = [
        backend_filters.DjangoFilterBackend,
        filters.SearchFilter,
    ]
    filterset_class = UserProfileFilter
    search_fields = ['first_name', 'last_name', 'user__username']
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = 'user__username'
    lookup_url_kwarg = 'username'

    def get_queryset(self):
        if self.action in ('list', 'retrieve'):
            return self.queryset.filter(user__is_active=True)
        return self.queryset.filter(user__is_active=True, user=self.request.user)
