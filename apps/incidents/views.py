
from rest_framework import generics

from apps.activity_logs.services import log_activity
from apps.users.permissions import IsAdministrator, IsResident

from .models import Incident
from .serializers import (
    IncidentSerializer,
    IncidentStatusUpdateSerializer,
)


class IncidentListCreateView(generics.ListCreateAPIView):
    serializer_class = IncidentSerializer
    permission_classes = [IsResident | IsAdministrator]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsResident()]

        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser or IsAdministrator().has_permission(
            self.request, self
        ):
            return Incident.objects.all()

        return Incident.objects.filter(reporter=user)

    def perform_create(self, serializer):
        incident = serializer.save(reporter=self.request.user)

        log_activity(
            user=self.request.user,
            action='INCIDENT_SUBMITTED',
            description=(
                f'{self.request.user.username} submitted a '
                f'{incident.incident_type} incident.'
            ),
            related_record_id=incident.pk,
        )


class IncidentDetailView(generics.RetrieveAPIView):
    serializer_class = IncidentSerializer
    permission_classes = [IsResident | IsAdministrator]
    lookup_field = 'pk'

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser or IsAdministrator().has_permission(
            self.request, self
        ):
            return Incident.objects.all()

        return Incident.objects.filter(reporter=user)


class IncidentStatusUpdateView(generics.UpdateAPIView):
    queryset = Incident.objects.all()
    serializer_class = IncidentStatusUpdateSerializer
    permission_classes = [IsAdministrator]
    http_method_names = ['patch', 'options']
    lookup_field = 'pk'

    def perform_update(self, serializer):
        incident = serializer.instance
        previous_status = incident.status

        incident = serializer.save()

        if previous_status != incident.status:
            log_activity(
                user=self.request.user,
                action='INCIDENT_STATUS_UPDATED',
                description=(
                    f'Incident {incident.pk} status changed from '
                    f'{previous_status} to {incident.status}.'
                ),
                related_record_id=incident.pk,
            )
