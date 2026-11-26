
from django.contrib.auth import authenticate, login, logout

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.activity_logs.services import log_activity

from .models import UserProfile
from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
)


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()

        log_activity(
            user=user,
            action='USER_REGISTERED',
            description=f'User {user.username} registered an account.',
            related_record_id=user.pk,
        )


class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'error': 'Username and password are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is None:
            return Response(
                {'error': 'Invalid username or password.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {'error': 'This account is inactive.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        login(request, user)

        profile = UserProfile.objects.filter(user=user).first()

        log_activity(
            user=user,
            action='USER_LOGIN',
            description=f'User {user.username} logged in.',
            related_record_id=user.pk,
        )

        response_data = {
            'message': 'Successfully logged in.',
            'id': str(user.pk),
            'username': user.username,
            'email': user.email,
            'role': profile.role if profile else None,
        }

        return Response(
            response_data,
            status=status.HTTP_200_OK,
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return UserProfile.objects.get(user=self.request.user)

    def perform_update(self, serializer):
        profile = serializer.save()

        log_activity(
            user=self.request.user,
            action='USER_PROFILE_UPDATED',
            description=f'User {self.request.user.username} updated their profile.',
            related_record_id=profile.pk,
        )


class UserLogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user

        log_activity(
            user=user,
            action='USER_LOGOUT',
            description=f'User {user.username} logged out.',
            related_record_id=user.pk,
        )

        logout(request)

        return Response(
            {'message': 'Successfully logged out.'},
            status=status.HTTP_200_OK,
        )

