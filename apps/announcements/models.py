from django.conf import settings
from django.db import models


class Announcement(models.Model):
    class Audience(models.TextChoices):
        ALL = 'ALL', 'Everyone'
        RESIDENTS = 'RESIDENTS', 'Residents'
        RESPONDERS = 'RESPONDERS', 'Responders'

    title = models.CharField(max_length=200)
    message = models.TextField()
    target_audience = models.CharField(
        max_length=20,
        choices=Audience.choices,
        default=Audience.ALL,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='announcements',
    )

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.title
