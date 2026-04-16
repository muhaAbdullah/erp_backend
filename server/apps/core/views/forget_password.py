import logging as loggers
from datetime import date
from django.conf import settings
from rest_framework import status
from django.db import transaction
from utils.threads import send_mail
from rest_framework import permissions
from apps.core.models import ForgetPassword
from apps.core.serializers import ForgetPasswordSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from apps.core.utils.reset_email_token_util import reset_email_token
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from rest_framework import serializers as drf_serializers


User = get_user_model()
loggers.basicConfig(level=loggers.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = loggers.getLogger(__name__)


class ForgetPasswordView(APIView):
    permission_classes = (permissions.AllowAny,)

    @extend_schema(
        tags=['Auth'],
        summary='Request password reset',
        description=(
            'Sends a password-reset link to the given email address. '
            'The link is valid for 15 minutes.'
        ),
        request=ForgetPasswordSerializer,
        responses={
            200: OpenApiResponse(
                description='Reset email sent.',
                response=inline_serializer(
                    name='ForgetPasswordSuccess',
                    fields={'message': drf_serializers.CharField()},
                ),
            ),
            400: OpenApiResponse(description='User not found.'),
        },
    )
    @transaction.atomic
    def post(self, request):
        try:
            serializer = ForgetPasswordSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            email = serializer.validated_data.get('email', None)
            user = get_object_or_404(User, email=email)
            token_exists = ForgetPassword.objects.filter(user__email=email)
            token_exists.delete()
            current_reset_token = reset_email_token(50)
            token = ForgetPassword.objects.create(user=user, token=current_reset_token)
            key = {
                'username': user.username,
                'button': settings.REACT_DOMAIN + settings.RESET_PASSWORD_URL + str(token.token),
                'year': date.today().year,
            }
            send_mail(
                subject="Reset Your Password",
                html_content="auth/forgetPassword.html",
                recipient_list=[email],
                key=key,
            )
            return Response({'message': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("%d", e)
            return Response({'message': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
