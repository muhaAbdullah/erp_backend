"""
Audit Log model for tracking all actions in the system.
"""
from django.db import models
from django.conf import settings
from coresite.mixin import BaseModel


class AuditLog(BaseModel):
    """
    Audit log for tracking all actions in the system.
    Automatically filtered by organization (except for super admins).
    """
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('ASSIGN_PERMISSION', 'Assign Permission'),
        ('REMOVE_PERMISSION', 'Remove Permission'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs',
        help_text='User who performed the action'
    )
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        help_text='Type of action performed'
    )
    model_name = models.CharField(
        max_length=100,
        help_text='Name of the model affected (e.g., User, Role, Organization)'
    )
    object_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text='ID of the affected object'
    )
    changes = models.JSONField(
        default=dict,
        help_text='JSON object storing before/after changes'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text='IP address of the client'
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
        help_text='Browser/client user agent string'
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['action', 'created_at']),
            models.Index(fields=['model_name', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.model_name} ({self.created_at})"
