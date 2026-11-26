
from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient

from apps.users.models import UserProfile
from .models import Announcement


User = get_user_model()


class AnnouncementManagementTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.admin = User.objects.create_user(
            username='announcement_admin',
            password='TestPassword123!',
        )

        UserProfile.objects.create(
            user=self.admin,
            role=UserProfile.Role.ADMINISTRATOR,
        )

        self.resident = User.objects.create_user(
            username='announcement_resident',
            password='TestPassword123!',
        )

        UserProfile.objects.create(
            user=self.resident,
            role=UserProfile.Role.RESIDENT,
        )

        self.responder = User.objects.create_user(
            username='announcement_responder',
            password='TestPassword123!',
        )

        UserProfile.objects.create(
            user=self.responder,
            role=UserProfile.Role.RESPONDER,
        )

        self.base_url = '/api/announcements/'

        self.all_announcement = self.create_announcement(
            'General Announcement',
            Announcement.Audience.ALL,
        )

        self.resident_announcement = self.create_announcement(
            'Resident Announcement',
            Announcement.Audience.RESIDENTS,
        )

        self.responder_announcement = self.create_announcement(
            'Responder Announcement',
            Announcement.Audience.RESPONDERS,
        )

        self.inactive_announcement = self.create_announcement(
            'Inactive Announcement',
            Announcement.Audience.ALL,
            is_active=False,
        )

    def create_announcement(
        self,
        title,
        audience,
        is_active=True,
    ):
        return Announcement.objects.create(
            title=title,
            message=f'Message for {title}',
            target_audience=audience,
            is_active=is_active,
            creator=self.admin,
        )

    def get_active_titles(self, client=None):
        if client is None:
            client = self.client

        response = client.get(
            f'{self.base_url}active/'
        )

        self.assertEqual(response.status_code, 200)

        return [item['title'] for item in response.data]

    def test_public_can_only_view_general_announcements(self):
        titles = self.get_active_titles()

        self.assertIn('General Announcement', titles)
        self.assertNotIn('Resident Announcement', titles)
        self.assertNotIn('Responder Announcement', titles)
        self.assertNotIn('Inactive Announcement', titles)

    def test_resident_sees_general_and_resident_announcements(self):
        self.client.force_authenticate(user=self.resident)

        titles = self.get_active_titles()

        self.assertIn('General Announcement', titles)
        self.assertIn('Resident Announcement', titles)
        self.assertNotIn('Responder Announcement', titles)
        self.assertNotIn('Inactive Announcement', titles)

    def test_responder_sees_general_and_responder_announcements(self):
        self.client.force_authenticate(user=self.responder)

        titles = self.get_active_titles()

        self.assertIn('General Announcement', titles)
        self.assertNotIn('Resident Announcement', titles)
        self.assertIn('Responder Announcement', titles)
        self.assertNotIn('Inactive Announcement', titles)

    def test_administrator_sees_all_active_announcements(self):
        self.client.force_authenticate(user=self.admin)

        titles = self.get_active_titles()

        self.assertIn('General Announcement', titles)
        self.assertIn('Resident Announcement', titles)
        self.assertIn('Responder Announcement', titles)
        self.assertNotIn('Inactive Announcement', titles)

    def test_administrator_can_create_announcement(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            self.base_url,
            {
                'title': 'Emergency Notice',
                'message': 'Emergency announcement message.',
                'target_audience': 'ALL',
                'is_active': True,
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)

        announcement = Announcement.objects.get(
            title='Emergency Notice',
        )

        self.assertEqual(announcement.creator, self.admin)

    def test_administrator_can_update_announcement(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            f'{self.base_url}{self.all_announcement.pk}/',
            {
                'title': 'Updated General Announcement',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)

        self.all_announcement.refresh_from_db()

        self.assertEqual(
            self.all_announcement.title,
            'Updated General Announcement',
        )

    def test_administrator_can_delete_announcement(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            f'{self.base_url}{self.all_announcement.pk}/',
        )

        self.assertEqual(response.status_code, 204)

        self.assertFalse(
            Announcement.objects.filter(
                pk=self.all_announcement.pk,
            ).exists()
        )

    def test_resident_cannot_create_announcement(self):
        self.client.force_authenticate(user=self.resident)

        response = self.client.post(
            self.base_url,
            {
                'title': 'Unauthorized Announcement',
                'message': 'This should not be allowed.',
                'target_audience': 'ALL',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 403)

    def test_responder_cannot_create_announcement(self):
        self.client.force_authenticate(user=self.responder)

        response = self.client.post(
            self.base_url,
            {
                'title': 'Unauthorized Announcement',
                'message': 'This should not be allowed.',
                'target_audience': 'ALL',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 403)
