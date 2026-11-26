from django.conf import settings
from django.db import models


class UserProfile(models.Model):

    class Role(models.TextChoices):
        RESIDENT = 'RESIDENT', 'Resident'
        RESPONDER = 'RESPONDER', 'Responder'
        ADMINISTRATOR = 'ADMINISTRATOR', 'Administrator'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.RESIDENT,
    )

    contact_number = models.CharField(
        max_length=20,
        blank=True,
        default='',
    )

    address = models.CharField(
        max_length=255,
        blank=True,
        default='',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} - {self.get_role_display()}'
