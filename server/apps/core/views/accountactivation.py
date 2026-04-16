import logging as logger
from rest_framework import status
from apps.core.models import UserActivation
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from datetime import datetime, timedelta
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse, inline_serializer
from rest_framework import serializers as drf_serializers


class AccountActivationAPIView(APIView):
    permission_classes = (AllowAny,)

    @extend_schema(
        tags=['Auth'],
        summary='Activate user account',
        description=(
            'Activates a user account using the secret key sent to the user\'s email. '
            'The token expires 30 minutes after registration.'
        ),
        parameters=[
            OpenApiParameter(
                name='secret_key',
                location=OpenApiParameter.PATH,
                description='50-character activation token sent to the user\'s email.',
                required=True,
                type=str,
            ),
        ],
        responses={
            200: OpenApiResponse(
                description='Account activated successfully.',
                response=inline_serializer(
                    name='ActivationSuccess',
                    fields={'message': drf_serializers.CharField(), 'status': drf_serializers.CharField()},
                ),
            ),
            400: OpenApiResponse(description='Already activated or invalid token.'),
            406: OpenApiResponse(description='User not found.'),
        },
    )
    def post(self, request, secret_key):
        try:
            user_activation = get_object_or_404(UserActivation, token=secret_key)
            print(user_activation.created_at + timedelta(minutes=3000000), "sdsdsds", timezone.now())
            if user_activation.created_at + timedelta(minutes=30) < timezone.now():
                return Response({"message": "Your activation token is expired."})

            if user_activation:
                if user_activation.user.is_active:
                    return Response({"message": "Account already activated", "status": "400"}, status=status.HTTP_400_BAD_REQUEST)
                if user_activation.token == secret_key and not user_activation.is_expired:
                    user_activation.user.is_active = True
                    user_activation.user.save()
                    user_activation.delete()
                    return Response({"message": "Account activated successfully", "status": "200"}, status=status.HTTP_200_OK)
                return Response({"message": "Account already activated", "status": "400"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "Invalid token", "status": "400"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(str(e))
            return Response({"message": "User Not Found", "status": "406"}, status.HTTP_406_NOT_ACCEPTABLE)
