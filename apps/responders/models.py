from django.conf import settings
from django.db import models


class ResponderProfile(models.Model):
    class Specialization(models.TextChoices):
        MEDICAL = 'MEDICAL', 'Medical'
        FIRE = 'FIRE', 'Fire'
        POLICE = 'POLICE', 'Police'
        GENERAL = 'GENERAL', 'General'

    class Availability(models.TextChoices):
        AVAILABLE = 'AVAILABLE', 'Available'
        ASSIGNED = 'ASSIGNED', 'Assigned'
        RESPONDING = 'RESPONDING', 'Responding'
        OFFLINE = 'OFFLINE', 'Offline'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='responder_profile',
    )
    specialization = models.CharField(
        max_length=10,
        choices=Specialization.choices,
    )
    contact_number = models.CharField(max_length=20)
    availability = models.CharField(
        max_length=10,
        choices=Availability.choices,
        default=Availability.OFFLINE,
    )
    assigned_area = models.CharField(max_length=150, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} - {self.get_specialization_display()}'
