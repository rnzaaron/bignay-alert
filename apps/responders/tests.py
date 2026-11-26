
from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient

from apps.users.models import UserProfile
from .models import ResponderProfile


User = get_user_model()


class ResponderManagementTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Create administrator
        self.admin = User.objects.create_user(
            username='responder_admin',
            password='TestPassword123!',
        )

        UserProfile.objects.create(
            user=self.admin,
            role=UserProfile.Role.ADMINISTRATOR,
        )

        # Create responder
        self.responder = User.objects.create_user(
            username='responder_test',
            password='TestPassword123!',
        )

        UserProfile.objects.create(
            user=self.responder,
            role=UserProfile.Role.RESPONDER,
        )

        self.responder_profile = ResponderProfile.objects.create(
            user=self.responder,
            specialization=ResponderProfile.Specialization.MEDICAL,
            contact_number='09123456789',
            availability=ResponderProfile.Availability.OFFLINE,
            assigned_area='Valenzuela City',
        )

        # Create resident
        self.resident = User.objects.create_user(
            username='resident_test',
            password='TestPassword123!',
        )

        UserProfile.objects.create(
            user=self.resident,
            role=UserProfile.Role.RESIDENT,
        )

        # Create another responder without a responder profile
        self.unassigned_responder = User.objects.create_user(
            username='unassigned_responder',
            password='TestPassword123!',
        )

        UserProfile.objects.create(
            user=self.unassigned_responder,
            role=UserProfile.Role.RESPONDER,
        )

        self.base_url = '/api/responders/'

    def test_administrator_can_view_responder_list(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(self.base_url)

        self.assertEqual(response.status_code, 200)

    def test_administrator_can_create_responder_profile(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            self.base_url,
            {
                'user': str(self.unassigned_responder.pk),
                'specialization': 'FIRE',
                'contact_number': '09987654321',
                'availability': 'AVAILABLE',
                'assigned_area': 'Malinta, Valenzuela',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)

        self.assertTrue(
            ResponderProfile.objects.filter(
                user=self.unassigned_responder,
            ).exists()
        )

    def test_administrator_can_view_responder_details(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            f'{self.base_url}{self.responder_profile.pk}/'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data['username'],
            'responder_test',
        )

    def test_administrator_can_update_responder_profile(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            f'{self.base_url}{self.responder_profile.pk}/',
            {
                'specialization': 'FIRE',
                'assigned_area': 'Marulas, Valenzuela',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)

        self.responder_profile.refresh_from_db()

        self.assertEqual(
            self.responder_profile.specialization,
            'FIRE',
        )

        self.assertEqual(
            self.responder_profile.assigned_area,
            'Marulas, Valenzuela',
        )

    def test_administrator_can_delete_responder_profile(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(
            f'{self.base_url}{self.responder_profile.pk}/'
        )

        self.assertEqual(response.status_code, 204)

        self.assertFalse(
            ResponderProfile.objects.filter(
                pk=self.responder_profile.pk,
            ).exists()
        )

    def test_responder_can_update_own_availability(self):
        self.client.force_authenticate(user=self.responder)

        response = self.client.patch(
            f'{self.base_url}me/availability/',
            {
                'availability': 'AVAILABLE',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)

        self.responder_profile.refresh_from_db()

        self.assertEqual(
            self.responder_profile.availability,
            'AVAILABLE',
        )

    def test_responder_without_profile_gets_not_found(self):
        self.client.force_authenticate(
            user=self.unassigned_responder,
        )

        response = self.client.patch(
            f'{self.base_url}me/availability/',
            {
                'availability': 'AVAILABLE',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 404)

    def test_resident_cannot_view_responder_list(self):
        self.client.force_authenticate(user=self.resident)

        response = self.client.get(self.base_url)

        self.assertEqual(response.status_code, 403)

    def test_resident_cannot_update_responder_availability(self):
        self.client.force_authenticate(user=self.resident)

        response = self.client.patch(
            f'{self.base_url}me/availability/',
            {
                'availability': 'AVAILABLE',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 403)

    def test_invalid_availability_is_rejected(self):
        self.client.force_authenticate(user=self.responder)

        response = self.client.patch(
            f'{self.base_url}me/availability/',
            {
                'availability': 'INVALID_STATUS',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 400)
