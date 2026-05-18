"""
Serializer for Religion model.
"""
from rest_framework import serializers
from apps.hrm.models import Religion


class ReligionSerializer(serializers.ModelSerializer):
    """
    Serializer for Religion model.
    Global master data - no organization linkage.
    """
    
    class Meta:
        model = Religion
        fields = ['id', 'name', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
