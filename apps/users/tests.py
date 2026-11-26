
from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient

from apps.activity_logs.models import ActivityLog
from .models import UserProfile
from .permissions import (
    IsResident,
    IsResponder,
    IsAdministrator,
)


User = get_user_model()


class UserRegistrationTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_resident_registration(self):
        response = self.client.post(
            '/api/users/register/',
            {
                'username': 'new_resident',
                'email': 'resident@example.com',
                'password': 'TestPassword123!',
                'contact_number': '09123456789',
                'address': 'Valenzuela City',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)

        user = User.objects.get(username='new_resident')
        profile = UserProfile.objects.get(user=user)

        self.assertEqual(profile.role, UserProfile.Role.RESIDENT)
        self.assertEqual(profile.contact_number, '09123456789')
        self.assertEqual(profile.address, 'Valenzuela City')

        self.assertTrue(
            ActivityLog.objects.filter(
                user=user,
                action='USER_REGISTERED',
                related_record_id=str(user.pk),
            ).exists()
        )


class UserAuthenticationTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username='auth_test_user',
            email='auth@example.com',
            password='TestPassword123!',
        )

        UserProfile.objects.create(
            user=self.user,
            role=UserProfile.Role.RESIDENT,
        )

    def test_successful_login(self):
        response = self.client.post(
            '/api/users/login/',
            {
                'username': 'auth_test_user',
                'password': 'TestPassword123!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['role'], 'RESIDENT')
        self.assertIsNotNone(self.client.session.session_key)

        self.assertTrue(
            ActivityLog.objects.filter(
                user=self.user,
                action='USER_LOGIN',
                related_record_id=str(self.user.pk),
            ).exists()
        )

    def test_invalid_login(self):
        response = self.client.post(
            '/api/users/login/',
            {
                'username': 'auth_test_user',
                'password': 'WrongPassword123!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 401)

    def test_missing_login_fields(self):
        response = self.client.post(
            '/api/users/login/',
            {},
            format='json',
        )

        self.assertEqual(response.status_code, 400)

    def test_successful_logout(self):
        self.client.force_login(self.user)

        response = self.client.post(
            '/api/users/logout/',
        )

        self.assertEqual(response.status_code, 200)

        self.assertTrue(
            ActivityLog.objects.filter(
                user=self.user,
                action='USER_LOGOUT',
                related_record_id=str(self.user.pk),
            ).exists()
        )

        profile_response = self.client.get(
            '/api/users/profile/',
        )

        self.assertEqual(profile_response.status_code, 403)


class UserProfileTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username='profile_test_user',
            email='profile@example.com',
            password='TestPassword123!',
        )

        UserProfile.objects.create(
            user=self.user,
            role=UserProfile.Role.RESIDENT,
            contact_number='09123456789',
            address='Valenzuela City',
        )

    def test_authenticated_user_can_view_profile(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            '/api/users/profile/',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], 'profile_test_user')

    def test_user_can_update_own_profile(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            '/api/users/profile/',
            {
                'contact_number': '09987654321',
                'address': 'Updated Valenzuela City',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)

        self.user.profile.refresh_from_db()

        self.assertEqual(
            self.user.profile.contact_number,
            '09987654321',
        )

        self.assertEqual(
            self.user.profile.address,
            'Updated Valenzuela City',
        )

        self.assertTrue(
            ActivityLog.objects.filter(
                user=self.user,
                action='USER_PROFILE_UPDATED',
                related_record_id=str(self.user.profile.pk),
            ).exists()
        )

    def test_unauthenticated_user_cannot_view_profile(self):
        response = self.client.get(
            '/api/users/profile/',
        )

        self.assertEqual(response.status_code, 403)


class RolePermissionTests(TestCase):

    def setUp(self):
        self.resident = User.objects.create_user(
            username='permission_resident',
            password='TestPassword123!',
        )

        self.responder = User.objects.create_user(
            username='permission_responder',
            password='TestPassword123!',
        )

        self.administrator = User.objects.create_user(
            username='permission_admin',
            password='TestPassword123!',
        )

        UserProfile.objects.create(
            user=self.resident,
            role=UserProfile.Role.RESIDENT,
        )

        UserProfile.objects.create(
            user=self.responder,
            role=UserProfile.Role.RESPONDER,
        )

        UserProfile.objects.create(
            user=self.administrator,
            role=UserProfile.Role.ADMINISTRATOR,
        )

    def test_resident_permissions(self):
        permission = IsResident()

        self.assertTrue(
            permission.has_permission(
                type('Request', (), {'user': self.resident})(),
                None,
            )
        )

        self.assertFalse(
            IsResponder().has_permission(
                type('Request', (), {'user': self.resident})(),
                None,
            )
        )

        self.assertFalse(
            IsAdministrator().has_permission(
                type('Request', (), {'user': self.resident})(),
                None,
            )
        )

    def test_responder_permissions(self):
        request = type('Request', (), {'user': self.responder})()

        self.assertTrue(IsResponder().has_permission(request, None))
        self.assertFalse(IsResident().has_permission(request, None))
        self.assertFalse(IsAdministrator().has_permission(request, None))

    def test_administrator_permissions(self):
        request = type('Request', (), {'user': self.administrator})()

        self.assertTrue(IsAdministrator().has_permission(request, None))
        self.assertFalse(IsResident().has_permission(request, None))
        self.assertFalse(IsResponder().has_permission(request, None))
