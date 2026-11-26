
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from .models import UserProfile


User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)

    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    contact_number = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    address = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'password',
            'contact_number',
            'address',
        )

    @transaction.atomic
    def create(self, validated_data):
        contact_number = validated_data.pop('contact_number', '')
        address = validated_data.pop('address', '')
        password = validated_data.pop('password')

        user = User.objects.create_user(
            password=password,
            **validated_data,
        )

        UserProfile.objects.create(
            user=user,
            role=UserProfile.Role.RESIDENT,
            contact_number=contact_number,
            address=address,
        )

        return user


class UserProfileSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)

    username = serializers.CharField(
        source='user.username',
        read_only=True,
    )

    email = serializers.EmailField(
        source='user.email',
        read_only=True,
    )

    class Meta:
        model = UserProfile
        fields = (
            'id',
            'username',
            'email',
            'role',
            'contact_number',
            'address',
            'created_at',
            'updated_at',
        )

        read_only_fields = (
            'id',
            'username',
            'email',
            'role',
            'created_at',
            'updated_at',
        )
