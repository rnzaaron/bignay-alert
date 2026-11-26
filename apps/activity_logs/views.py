from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.users.permissions import IsAdministrator

from .models import ActivityLog
from .serializers import ActivityLogSerializer


class ActivityLogViewSet(ReadOnlyModelViewSet):
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer
    permission_classes = (IsAdministrator,)