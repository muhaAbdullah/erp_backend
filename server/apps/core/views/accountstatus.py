from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from rest_framework import serializers as drf_serializers

User = get_user_model()


class AccountStatusAPIView(APIView):
    permission_classes = (AllowAny,)

    @extend_schema(
        tags=['Auth'],
        summary='Check account status',
        description=(
            'Returns whether the account for the given email is active, '
            'along with the user\'s type (user / admin / super_admin).'
        ),
        request=inline_serializer(
            name='AccountStatusRequest',
            fields={'email': drf_serializers.EmailField()},
        ),
        responses={
            200: OpenApiResponse(
                description='Account status returned.',
                response=inline_serializer(
                    name='AccountStatusResponse',
                    fields={
                        'message': drf_serializers.BooleanField(),
                        'status': drf_serializers.CharField(),
                        'user_type': drf_serializers.CharField(),
                    },
                ),
            ),
            404: OpenApiResponse(description='User not found.'),
            500: OpenApiResponse(description='Internal server error.'),
        },
    )
    def post(self, request):
        try:
            user = get_object_or_404(User, email=request.data['email'])
            if user.is_active:
                return Response({"message": True, "status": "200", "user_type": user.user_type}, status=status.HTTP_200_OK)
            return Response({'message': False, "status": "200", "user_type": user.user_type}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e), "status": "500"}, status.HTTP_500_INTERNAL_SERVER_ERROR)
