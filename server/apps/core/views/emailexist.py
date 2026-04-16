from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from rest_framework import serializers as drf_serializers

User = get_user_model()


class EmailExistAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Auth'],
        summary='Check if email exists',
        description='Returns whether the given email address is already registered in the system.',
        request=inline_serializer(
            name='EmailExistRequest',
            fields={'email': drf_serializers.EmailField()},
        ),
        responses={
            200: OpenApiResponse(
                description='Email exists.',
                response=inline_serializer(
                    name='EmailExistTrue',
                    fields={'message': drf_serializers.BooleanField(), 'status': drf_serializers.CharField()},
                ),
            ),
            400: OpenApiResponse(description='Email does not exist.'),
            500: OpenApiResponse(description='Internal server error.'),
        },
    )
    def post(self, request):
        try:
            if User.objects.filter(email=request.data['email']).exists():
                return Response({"message": True, "status": "200"}, status=status.HTTP_200_OK)
            return Response({'message': False, "status": "400"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": str(e), "status": "500"}, status.HTTP_500_INTERNAL_SERVER_ERROR)
