"""
URL configuration for HRM app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EmployeeViewSet, EmployeePersonalViewSet, EmployeeContactViewSet,
    EmployeeGovernmentViewSet, DepartmentViewSet, DesignationViewSet,
    ShiftViewSet, EmployeeTypeViewSet, ScaleCategoryViewSet,
    ReligionViewSet, QualificationViewSet
)

# Create router and register viewsets
router = DefaultRouter()

# Employee related endpoints
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'employee-personal', EmployeePersonalViewSet, basename='employee-personal')
router.register(r'employee-contact', EmployeeContactViewSet, basename='employee-contact')
router.register(r'employee-government', EmployeeGovernmentViewSet, basename='employee-government')

# Master data endpoints (organization-specific)
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'designations', DesignationViewSet, basename='designation')
router.register(r'shifts', ShiftViewSet, basename='shift')
router.register(r'employee-types', EmployeeTypeViewSet, basename='employee-type')
router.register(r'scale-categories', ScaleCategoryViewSet, basename='scale-category')

# Global master data endpoints (no organization)
router.register(r'religions', ReligionViewSet, basename='religion')
router.register(r'qualifications', QualificationViewSet, basename='qualification')

urlpatterns = [
    path('', include(router.urls)),
]
