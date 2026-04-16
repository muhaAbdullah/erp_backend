from django_filters import rest_framework as filters

from apps.userprofile.models import UserProfile


class UserProfileFilter(filters.FilterSet):
    class Meta:
        model = UserProfile
        fields = [
            'user', 'user__user_type', 'user__is_active',
            'user__is_staff', 'user__is_superuser', 'user__email'

        ]
