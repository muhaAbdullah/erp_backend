from datetime import date
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from utils.threads.email_thread import send_mail
from apps.core.serializers import ChangePasswordSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from rest_framework import serializers as drf_serializers

User = get_user_model()


class ChangePasswordView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = ChangePasswordSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

    @extend_schema(
        tags=['User'],
        summary='Change password',
        description=(
            'Changes the password of the currently authenticated user. '
            'Requires the current password for verification. '
            'A confirmation email is sent after a successful change.'
        ),
        request=ChangePasswordSerializer,
        responses={
            200: OpenApiResponse(
                description='Password updated successfully.',
                response=inline_serializer(
                    name='ChangePasswordSuccess',
                    fields={
                        'status': drf_serializers.CharField(),
                        'code': drf_serializers.IntegerField(),
                        'message': drf_serializers.CharField(),
                    },
                ),
            ),
            400: OpenApiResponse(description='Wrong old password or validation error.'),
        },
    )
    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()

            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
            }
            key = {
                'username': self.object.username,
                'button': settings.REACT_DOMAIN + 'auth/login',
                'year': date.today().year,
            }
            send_mail(
                subject="Password Changed",
                html_content="auth/passwordChanged.html",
                recipient_list=[self.object.email],
                key=key,
            )
            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
