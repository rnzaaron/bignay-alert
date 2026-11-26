from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import ActivityLog
from .serializers import ActivityLogSerializer


class ActivityLogViewSet(ReadOnlyModelViewSet):
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer
    permission_classes = (IsAdminUser,)
