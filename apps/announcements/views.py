
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.activity_logs.services import log_activity
from apps.users.models import UserProfile
from apps.users.permissions import IsAdministrator

from .models import Announcement
from .serializers import AnnouncementSerializer


class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = (IsAdministrator,)

    def get_permissions(self):
        if self.action == 'active':
            return [AllowAny()]

        return super().get_permissions()

    def perform_create(self, serializer):
        announcement = serializer.save(creator=self.request.user)

        log_activity(
            user=self.request.user,
            action='ANNOUNCEMENT_CREATED',
            description=(
                f'{self.request.user.username} created an announcement: '
                f'{announcement.title}.'
            ),
            related_record_id=announcement.pk,
        )

    def perform_update(self, serializer):
        announcement = serializer.save()

        log_activity(
            user=self.request.user,
            action='ANNOUNCEMENT_UPDATED',
            description=(
                f'{self.request.user.username} updated announcement: '
                f'{announcement.title}.'
            ),
            related_record_id=announcement.pk,
        )

    def perform_destroy(self, instance):
        announcement_id = instance.pk
        announcement_title = instance.title

        instance.delete()

        log_activity(
            user=self.request.user,
            action='ANNOUNCEMENT_DELETED',
            description=(
                f'{self.request.user.username} deleted announcement: '
                f'{announcement_title}.'
            ),
            related_record_id=announcement_id,
        )

    @action(detail=False, methods=('get',), url_path='active')
    def active(self, request):
        announcements = self.get_queryset().filter(
            is_active=True,
        )

        # Determine which announcements the current user may receive.
        if request.user.is_authenticated:
            if request.user.is_superuser:
                allowed_audiences = [
                    Announcement.Audience.ALL,
                    Announcement.Audience.RESIDENTS,
                    Announcement.Audience.RESPONDERS,
                ]
            else:
                role = UserProfile.objects.filter(
                    user=request.user,
                ).values_list('role', flat=True).first()

                if role == UserProfile.Role.ADMINISTRATOR:
                    allowed_audiences = [
                        Announcement.Audience.ALL,
                        Announcement.Audience.RESIDENTS,
                        Announcement.Audience.RESPONDERS,
                    ]
                elif role == UserProfile.Role.RESIDENT:
                    allowed_audiences = [
                        Announcement.Audience.ALL,
                        Announcement.Audience.RESIDENTS,
                    ]
                elif role == UserProfile.Role.RESPONDER:
                    allowed_audiences = [
                        Announcement.Audience.ALL,
                        Announcement.Audience.RESPONDERS,
                    ]
                else:
                    allowed_audiences = [
                        Announcement.Audience.ALL,
                    ]
        else:
            allowed_audiences = [
                Announcement.Audience.ALL,
            ]

        announcements = announcements.filter(
            target_audience__in=allowed_audiences,
        )

        serializer = self.get_serializer(
            announcements,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
