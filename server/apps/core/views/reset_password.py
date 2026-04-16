from rest_framework import status
import logging as logger
from apps.core.models import ForgetPassword
from rest_framework.views import APIView
from apps.core.serializers import ResetPasswordSerializer
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from datetime import datetime, timedelta, timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, inline_serializer
from rest_framework import serializers as drf_serializers

User = get_user_model()


class ResetPasswordAPIView(APIView):
    permission_classes = (AllowAny,)

    @extend_schema(
        tags=['Auth'],
        summary='Reset password',
        description=(
            'Sets a new password for the user identified by the reset token. '
            'The token must be used within 15 minutes of being issued.'
        ),
        parameters=[
            OpenApiParameter(
                name='secret_key',
                location=OpenApiParameter.PATH,
                description='50-character password-reset token sent to the user\'s email.',
                required=True,
                type=str,
            ),
        ],
        request=ResetPasswordSerializer,
        responses={
            200: OpenApiResponse(
                description='Password reset successfully.',
                response=inline_serializer(
                    name='ResetPasswordSuccess',
                    fields={'message': drf_serializers.CharField()},
                ),
            ),
            400: OpenApiResponse(description='Expired or invalid token.'),
            406: OpenApiResponse(description='Unexpected error.'),
        },
    )
    def post(self, request, secret_key):
        try:
            token = get_object_or_404(ForgetPassword, token=secret_key)
            if (token.created_at + timedelta(minutes=15)).replace(tzinfo=timezone.utc) < datetime.now(timezone.utc) - timedelta(minutes=15):
                token.activated = False
                token.is_expired = True
                token.save()
                return Response({"message": "Your token is expired"}, status=status.HTTP_400_BAD_REQUEST)
            if token.token == secret_key and token.activated and not token.is_expired:
                serializer = ResetPasswordSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                password = serializer.validated_data.get('password', None)
                token.user.set_password(password)
                token.user.save()
                token.delete()
                return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)
            return Response({"message": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(str(e))
            return Response({"message": "Something went wrong."}, status.HTTP_406_NOT_ACCEPTABLE)
