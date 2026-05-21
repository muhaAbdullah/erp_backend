"""
Mixin to enforce organization assignment from logged-in user.
Prevents accepting organization from API requests for security.
"""


class EnforceOrganizationMixin:
    """
    Mixin to enforce organization assignment from logged-in user.
    
    This mixin ensures that all created objects automatically get assigned
    to the logged-in user's organization, preventing API clients from
    specifying a different organization (tenant isolation enforcement).
    
    Usage:
        class MyViewSet(EnforceOrganizationMixin, viewsets.ModelViewSet):
            # ... rest of viewset configuration
    
    Important:
        - This should NOT be used for registration endpoints
        - Super admins can still create objects for any organization if needed
        - Apply this to all ViewSets that have an organization field
    """
    
    def perform_create(self, serializer):
        """
        Override perform_create to always set organization from request user.
        Super admins can specify organization_id; regular users get auto-assigned.
        
        Args:
            serializer: DRF serializer instance
        """
        # For super admin, allow specifying organization_id if provided
        if self.request.user.is_super_admin and 'organization_id' in serializer.validated_data:
            # Super admin can set organization explicitly via organization_id
            from apps.core.models import Organization
            org_id = serializer.validated_data.pop('organization_id')
            organization = Organization.objects.get(id=org_id)
            serializer.save(organization=organization)
        else:
            # Regular users: force organization from their account, ignore any organization_id
            serializer.validated_data.pop('organization_id', None)
            serializer.save(organization=self.request.user.organization)
