
from django.urls import path, include
from django.urls import re_path
from .views import UserProfileViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('user-profile', UserProfileViewSet, basename='userprofile')

urlpatterns = [
    path('', include(router.urls)),

]
