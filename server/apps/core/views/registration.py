from datetime import date
from django.conf import settings
from rest_framework import status
from django.db import transaction
from rest_framework import permissions
from apps.core.models import UserActivation
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from utils.threads.email_thread import send_mail
from apps.core.serializers import CreateUserSerializer
from apps.userprofile.serializers import UserProfileSerializer
from apps.core.utils.reset_email_token_util import reset_email_token
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from rest_framework import serializers as drf_serializers


User = get_user_model()
email = settings.EMAIL_HOST_USER
react_domain = settings.REACT_DOMAIN


class RegistrationView(APIView):
    permission_classes = (permissions.AllowAny,)

    @extend_schema(
        tags=['Auth'],
        summary='Register a new user',
        description=(
            'Creates a new user account and sends a verification email. '
            'The account remains inactive until the user clicks the activation link.'
        ),
        request=CreateUserSerializer,
        responses={
            201: OpenApiResponse(
                description='User created successfully.',
                response=inline_serializer(
                    name='RegisterSuccess',
                    fields={'message': drf_serializers.CharField()},
                ),
            ),
            400: OpenApiResponse(description='Validation error.'),
        },
    )
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = serializer.validated_data.pop('profile', None)
        serializer.save()
        instance = serializer.instance
        if profile:
            profile_serializer = UserProfileSerializer(data=profile)
            profile_serializer.is_valid(raise_exception=True)
            profile_serializer.save(user=instance)

        secret_key = reset_email_token(50)
        UserActivation(user=instance, token=secret_key).save()

        key = {
            'username': instance.username,
            'otp': None,
            'button': react_domain + '/api/user/account-activation/' + secret_key,
            'year': date.today().year,
        }

        send_mail(
            subject="Verify Your Account",
            html_content="auth/new_userRegister.html",
            recipient_list=[request.data['email']],
            key=key,
        )

        return Response({
            "message": "User created successfully. Check your email for verification"
        }, status=status.HTTP_201_CREATED)
