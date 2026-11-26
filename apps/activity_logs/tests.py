from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient

from apps.users.models import UserProfile
from .models import ActivityLog
from .services import log_activity


User = get_user_model()


class ActivityLogServiceTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='activity_test_user',
            password='TestPassword123!',
        )

    def test_create_activity_log(self):
        log = log_activity(
            user=self.user,
            action='USER_LOGIN',
            description='User logged in successfully.',
        )

        self.assertEqual(log.user, self.user)
        self.assertEqual(log.action, 'USER_LOGIN')
        self.assertEqual(
            log.description,
            'User logged in successfully.',
        )

    def test_action_is_stripped(self):
        log = log_activity(
            user=self.user,
            action='  USER_LOGIN  ',
            description='User logged in.',
        )

        self.assertEqual(log.action, 'USER_LOGIN')

    def test_related_record_id_is_converted_to_string(self):
        log = log_activity(
            user=self.user,
            action='INCIDENT_UPDATED',
            description='Incident status updated.',
            related_record_id=12345,
        )

        self.assertEqual(log.related_record_id, '12345')

    def test_missing_related_record_id_becomes_empty_string(self):
        log = log_activity(
            user=self.user,
            action='USER_LOGIN',
            description='User logged in.',
        )

        self.assertEqual(log.related_record_id, '')

    def test_empty_action_is_rejected(self):
        with self.assertRaises(ValueError):
            log_activity(
                user=self.user,
                action='   ',
                description='User logged in.',
            )

    def test_empty_description_is_rejected(self):
        with self.assertRaises(ValueError):
            log_activity(
                user=self.user,
                action='USER_LOGIN',
                description='   ',
            )


class ActivityLogAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.admin = User.objects.create_user(
            username='activity_admin',
            password='TestPassword123!',
        )
        UserProfile.objects.create(
            user=self.admin,
            role=UserProfile.Role.ADMINISTRATOR,
        )

        self.resident = User.objects.create_user(
            username='activity_resident',
            password='TestPassword123!',
        )
        UserProfile.objects.create(
            user=self.resident,
            role=UserProfile.Role.RESIDENT,
        )

        self.log = ActivityLog.objects.create(
            user=self.admin,
            action='USER_LOGIN',
            description='Administrator logged in.',
            related_record_id='123',
        )

        self.base_url = '/api/activity-logs/'

    def test_administrator_can_view_activity_logs(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(self.base_url)

        self.assertEqual(response.status_code, 200)

    def test_resident_cannot_view_activity_logs(self):
        self.client.force_authenticate(user=self.resident)

        response = self.client.get(self.base_url)

        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_user_cannot_view_activity_logs(self):
        response = self.client.get(self.base_url)

        self.assertIn(response.status_code, [401, 403])

    def test_activity_logs_are_read_only(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            self.base_url,
            {
                'action': 'USER_LOGIN',
                'description': 'Attempt to create through API.',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 405)