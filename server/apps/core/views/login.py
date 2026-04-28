"""
Custom login view with audit logging.
"""
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
from apps.core.utils.audit_logger import log_action
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom Token Obtain Pair View that logs user login attempts.
    """
    
    def post(self, request, *args, **kwargs):
        """Override post to add audit logging for successful logins."""
        response = super().post(request, *args, **kwargs)
        
        # Log successful login
        if response.status_code == status.HTTP_200_OK:
            # Get user from email/username in request
            email_or_username = request.data.get('email') or request.data.get('username')
            
            try:
                # Try to find user by email or username
                user = None
                if '@' in str(email_or_username):
                    user = User.objects.get(email=email_or_username)
                else:
                    user = User.objects.get(username=email_or_username)
                
                # Log the login
                log_action(
                    user=user,
                    action='LOGIN',
                    model_name='User',
                    object_id=user.id,
                    changes={},
                    request=request
                )
            except User.DoesNotExist:
                pass  # User not found, skip logging
        
        return response
