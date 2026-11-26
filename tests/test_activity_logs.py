from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.activity_logs.services import log_activity


class ActivityLogAPITests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.admin = user_model.objects.create_user(
            username='activity-admin',
            password='test-password',
            is_staff=True,
        )
        self.user = user_model.objects.create_user(
            username='activity-user',
            password='test-password',
        )
        self.logs_url = '/api/activity-logs/'

    def test_backend_log_is_visible_to_admin(self):
        log = log_activity(
            user=self.user,
            action='announcement.created',
            description='Published an announcement.',
            related_record_id='announcement-123',
        )
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(self.logs_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], str(log.pk))
        self.assertEqual(response.data[0]['user'], self.user.username)
        self.assertEqual(
            response.data[0]['related_record_id'],
            'announcement-123',
        )

        create_response = self.client.post(
            self.logs_url,
            {'action': 'forged', 'description': 'Forged from browser'},
            format='json',
        )
        self.assertEqual(
            create_response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_activity_log_list_is_admin_only(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.logs_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
