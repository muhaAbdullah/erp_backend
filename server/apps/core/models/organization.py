from django.db import models
from coresite.mixin import AbstractTimeStampModel


class Organization(AbstractTimeStampModel):
    """
    Organization model for multi-tenancy support.
    Each user and most other models belong to an organization.
    """
    name = models.CharField(max_length=255, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'
        ordering = ['name']

    def __str__(self):
        return self.name
