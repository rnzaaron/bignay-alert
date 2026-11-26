from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from .models import Announcement
from .serializers import AnnouncementSerializer


class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = (IsAdminUser,)

    def get_permissions(self):
        if self.action == 'active':
            return [AllowAny()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(detail=False, methods=('get',), url_path='active')
    def active(self, request):
        announcements = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(announcements, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
