from rest_framework import serializers

from .models import ActivityLog


class ActivityLogSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    user = serializers.CharField(
        source='user.username',
        read_only=True,
        allow_null=True,
    )
    user_id = serializers.CharField(read_only=True, allow_null=True)

    class Meta:
        model = ActivityLog
        fields = (
            'id',
            'user',
            'user_id',
            'action',
            'description',
            'related_record_id',
            'timestamp',
        )
        read_only_fields = fields