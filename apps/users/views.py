
from django.contrib.auth import authenticate, login, logout

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import UserProfile
from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
)


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


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


class UserLogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)

        return Response(
            {'message': 'Successfully logged out.'},
            status=status.HTTP_200_OK,
        )
