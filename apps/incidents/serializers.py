from rest_framework import serializers

from .models import Incident


class IncidentSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    reporter = serializers.CharField(source='reporter.username', read_only=True)

    class Meta:
        model = Incident
        fields = (
            'id',
            'reporter',
            'incident_type',
            'description',
            'location',
            'latitude',
            'longitude',
            'status',
            'cancellation_reason',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'reporter',
            'status',
            'cancellation_reason',
            'created_at',
            'updated_at',
        )


class IncidentStatusUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Incident
        fields = (
            'status',
            'cancellation_reason',
        )

    def validate(self, attrs):
        new_status = attrs.get(
            'status',
            self.instance.status if self.instance else None,
        )

        cancellation_reason = attrs.get(
            'cancellation_reason',
            self.instance.cancellation_reason if self.instance else '',
        )

        if new_status == 'CANCELLED' and not cancellation_reason.strip():
            raise serializers.ValidationError({
                'cancellation_reason': 'A reason is required when cancelling an incident.'
            })

        return attrs
