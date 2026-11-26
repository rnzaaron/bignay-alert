
from rest_framework.permissions import BasePermission

from .models import UserProfile


class HasUserRole(BasePermission):
    required_role = None

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # Allow Django superusers administrative access.
        if user.is_superuser:
            return True

        return UserProfile.objects.filter(
            user=user,
            role=self.required_role,
        ).exists()


class IsResident(HasUserRole):
    required_role = UserProfile.Role.RESIDENT


class IsResponder(HasUserRole):
    required_role = UserProfile.Role.RESPONDER


class IsAdministrator(HasUserRole):
    required_role = UserProfile.Role.ADMINISTRATOR
