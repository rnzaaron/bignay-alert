from rest_framework import serializers

from .models import Announcement


class AnnouncementSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    creator = serializers.CharField(
        source='creator.username',
        read_only=True,
        allow_null=True,
    )
    creator_id = serializers.CharField(read_only=True, allow_null=True)

    class Meta:
        model = Announcement
        fields = (
            'id',
            'title',
            'message',
            'target_audience',
            'is_active',
            'created_at',
            'updated_at',
            'creator',
            'creator_id',
        )
        read_only_fields = (
            'id',
            'created_at',
            'updated_at',
            'creator',
            'creator_id',
        )