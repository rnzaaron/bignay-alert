from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase


class AnnouncementAPITests(APITestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_user(
            username='announcement-admin',
            password='test-password',
            is_staff=True,
        )
        self.announcements_url = '/api/announcements/'
        self.active_url = f'{self.announcements_url}active/'

    def test_admin_can_create_update_and_publish_announcement(self):
        self.client.force_authenticate(user=self.admin)

        create_response = self.client.post(
            self.announcements_url,
            {
                'title': 'Road closure',
                'message': 'Main street is closed today.',
                'target_audience': 'RESIDENTS',
                'creator_id': 'untrusted-user-id',
            },
            format='json',
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        announcement_id = create_response.data['id']
        self.assertEqual(
            create_response.data['creator'],
            self.admin.username,
        )
        self.assertTrue(create_response.data['is_active'])

        self.client.force_authenticate(user=None)
        active_response = self.client.get(self.active_url)
        self.assertEqual(active_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(active_response.data), 1)

        self.client.force_authenticate(user=self.admin)
        update_response = self.client.patch(
            f'{self.announcements_url}{announcement_id}/',
            {'is_active': False},
            format='json',
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=None)
        active_response = self.client.get(self.active_url)
        self.assertEqual(active_response.data, [])

    def test_non_admin_cannot_create_announcements(self):
        user = get_user_model().objects.create_user(
            username='announcement-resident',
            password='test-password',
        )
        self.client.force_authenticate(user=user)

        response = self.client.post(
            self.announcements_url,
            {
                'title': 'Untrusted',
                'message': 'Untrusted message',
                'target_audience': 'ALL',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)