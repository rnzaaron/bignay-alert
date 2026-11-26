from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import ResponderProfile


class ResponderProfileSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model()._default_manager.all(),
        pk_field=serializers.CharField(),
    )
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = ResponderProfile
        fields = (
            'id',
            'user',
            'username',
            'specialization',
            'contact_number',
            'availability',
            'assigned_area',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'username', 'created_at', 'updated_at')


class ResponderAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ResponderProfile
        fields = ('availability',)
