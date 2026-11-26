
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.activity_logs.services import log_activity
from apps.users.permissions import IsAdministrator, IsResponder

from .models import ResponderProfile
from .serializers import (
    ResponderAvailabilitySerializer,
    ResponderProfileSerializer,
)


class ResponderProfileViewSet(viewsets.ModelViewSet):
    queryset = ResponderProfile.objects.all()
    serializer_class = ResponderProfileSerializer
    permission_classes = (IsAdministrator,)

    def get_permissions(self):
        if self.action == 'update_own_availability':
            return [IsResponder()]

        return super().get_permissions()

    def perform_create(self, serializer):
        profile = serializer.save()

        log_activity(
            user=self.request.user,
            action='RESPONDER_PROFILE_CREATED',
            description=(
                f'{self.request.user.username} created a responder profile.'
            ),
            related_record_id=profile.pk,
        )

    def perform_update(self, serializer):
        profile = serializer.save()

        log_activity(
            user=self.request.user,
            action='RESPONDER_PROFILE_UPDATED',
            description=(
                f'{self.request.user.username} updated a responder profile.'
            ),
            related_record_id=profile.pk,
        )

    def perform_destroy(self, instance):
        profile_id = instance.pk

        instance.delete()

        log_activity(
            user=self.request.user,
            action='RESPONDER_PROFILE_DELETED',
            description=(
                f'{self.request.user.username} deleted a responder profile.'
            ),
            related_record_id=profile_id,
        )

    @action(detail=False, methods=('patch',), url_path='me/availability')
    def update_own_availability(self, request):
        profile = get_object_or_404(
            ResponderProfile,
            user=request.user,
        )

        previous_availability = profile.availability

        serializer = ResponderAvailabilitySerializer(
            profile,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)
        profile = serializer.save()

        if previous_availability != profile.availability:
            log_activity(
                user=request.user,
                action='RESPONDER_AVAILABILITY_UPDATED',
                description=(
                    f'{request.user.username} changed availability from '
                    f'{previous_availability} to {profile.availability}.'
                ),
                related_record_id=profile.pk,
            )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
