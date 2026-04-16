from rest_framework import permissions
from rest_framework import generics
from django.contrib.auth import get_user_model
from apps.core.serializers import UserDetailSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view

User = get_user_model()


@extend_schema_view(
    get=extend_schema(
        tags=['User'],
        summary='Get current user',
        description='Returns the profile details of the currently authenticated user.',
    ),
    put=extend_schema(
        tags=['User'],
        summary='Update current user',
        description='Fully updates the profile of the currently authenticated user.',
    ),
    patch=extend_schema(
        tags=['User'],
        summary='Partial update current user',
        description='Partially updates the profile of the currently authenticated user.',
    ),
    delete=extend_schema(
        tags=['User'],
        summary='Delete current user',
        description='Deletes the account of the currently authenticated user.',
    ),
)
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user
