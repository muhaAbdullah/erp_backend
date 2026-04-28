from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.userprofile.serializers import UserProfileSerializer
from apps.core.validators import validate_role_organization

User = get_user_model()


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for User details with role-organization validation.
    
    Organization is read-only to prevent users from changing their organization.
    Role assignment is validated to ensure it belongs to the user's organization.
    """
    profile = UserProfileSerializer(required=False)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'user_type', 'is_active', 'is_super_admin',
            'organization', 'organization_name', 'role', 'role_name',
            'permissions', 'profile', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'organization', 'organization_name', 'is_super_admin',
                           'permissions', 'created_at', 'updated_at']
    
    def get_permissions(self, obj):
        """Get user's permission codes."""
        from apps.core.utils.permission_helper import get_user_permissions
        return list(get_user_permissions(obj))
    
    def validate_role(self, value):
        """
        Validate that role belongs to user's organization.
        """
        if not value:
            return value
        
        # Get the user being updated
        user = self.instance
        if user:
            validate_role_organization(user, value)
        
        return value

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        
        # Validate role if being updated
        if 'role' in validated_data:
            validate_role_organization(instance, validated_data['role'])

        #  Update User fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        #  Update Profile (nested)
        if profile_data:
            profile = getattr(instance, 'profile', None)

            if profile:  # existing profile
                for attr, value in profile_data.items():
                    setattr(profile, attr, value)
                profile.save()
            else:
                # optional: create profile if not exists
                from apps.userprofile.models import UserProfile
                UserProfile.objects.create(user=instance, **profile_data)

        return instance