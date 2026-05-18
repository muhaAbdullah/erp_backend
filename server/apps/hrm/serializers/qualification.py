"""
Serializer for Qualification model.
"""
from rest_framework import serializers
from apps.hrm.models import Qualification


class QualificationSerializer(serializers.ModelSerializer):
    """
    Serializer for Qualification model.
    Global master data - no organization linkage.
    """
    
    class Meta:
        model = Qualification
        fields = ['id', 'code', 'name', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
