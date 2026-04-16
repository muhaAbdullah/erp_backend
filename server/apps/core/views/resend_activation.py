from datetime import date
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from apps.core.models import UserActivation
from apps.core.serializers import ResendEmailSerializer
from apps.core.utils.reset_email_token_util import reset_email_token
from utils.threads.email_thread import send_mail
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from rest_framework import serializers as drf_serializers

User = get_user_model()
domain = settings.DOMAIN


class ResendActivationAPIView(APIView):
    permission_classes = (AllowAny,)

    @extend_schema(
        tags=['Auth'],
        summary='Resend activation email',
        description=(
            'Resends the account activation email to the given address. '
            'Only valid for accounts that have not yet been activated.'
        ),
        request=ResendEmailSerializer,
        responses={
            200: OpenApiResponse(
                description='Activation email sent.',
                response=inline_serializer(
                    name='ResendActivationSuccess',
                    fields={'message': drf_serializers.CharField()},
                ),
            ),
            400: OpenApiResponse(description='Account already activated or not found.'),
        },
    )
    def post(self, request, *args, **kwargs):
        try:
            serializer = ResendEmailSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            email = serializer.validated_data.get('email', None)
            user = get_object_or_404(User, user__email=email)
            if user.is_active:
                return Response({"message": "Account already activated"},
                                status=status.HTTP_400_BAD_REQUEST)
            user_activation = user.user_activation
            if user_activation:
                user_activation.delete()
            secret_key = reset_email_token(50)
            UserActivation.objects.create(user=user, secret_key=secret_key)
            key = {
                'username': user.username,
                'otp': None,
                'button': domain + '/api/user/account-activation/' + secret_key,
                'year': date.today().year,
            }

            send_mail(
                subject="Verify Your Account",
                html_content="auth/new_userRegister.html",
                recipient_list=[email],
                key=key,
            )

            return Response({"message": "New OTP sent successfully. Check your email for verification"},
                            status=status.HTTP_200_OK)
        except UserActivation.DoesNotExist:
            return Response({"message": "User not found or account already activated"},
                            status=status.HTTP_400_BAD_REQUEST)
