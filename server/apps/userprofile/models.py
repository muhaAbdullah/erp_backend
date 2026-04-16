from django.db import models
from apps.core.models import User
from coresite.mixin import AbstractTimeStampModel


class UserProfile(AbstractTimeStampModel):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='images', blank=True, null=True)

    def __str__(self):
        return self.first_name+' '+self.last_name

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
