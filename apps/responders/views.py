from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .models import ResponderProfile
from .serializers import (
    ResponderAvailabilitySerializer,
    ResponderProfileSerializer,
)


class ResponderProfileViewSet(viewsets.ModelViewSet):
    queryset = ResponderProfile.objects.all()
    serializer_class = ResponderProfileSerializer
    permission_classes = (IsAdminUser,)

    def get_permissions(self):
        if self.action == 'update_own_availability':
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(detail=False, methods=('patch',), url_path='me/availability')
    def update_own_availability(self, request):
        profile = get_object_or_404(
            ResponderProfile,
            user=request.user,
        )
        serializer = ResponderAvailabilitySerializer(
            profile,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
