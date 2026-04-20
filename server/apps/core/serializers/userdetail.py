from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.userprofile.serializers import UserProfileSerializer

User = get_user_model()


class UserDetailSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ['username', 'email',  'user_type', 'profile']

    def update(self, instance, validated_data):
            profile_data = validated_data.pop('profile', None)

            # 🔹 Update User fields
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            # 🔹 Update Profile (nested)
            if profile_data:
                profile = getattr(instance, 'profile', None)

                if profile:  # existing profile
                    for attr, value in profile_data.items():
                        setattr(profile, attr, value)
                    profile.save()
                else:
                    # optional: create profile if not exists
                    UserProfile.objects.create(user=instance, **profile_data)

            return instance