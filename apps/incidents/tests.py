from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import UserProfile

from .models import Incident


User = get_user_model()


class IncidentAPITests(APITestCase):

    def setUp(self):
        self.resident = User.objects.create_user(
            username='incident_resident_001',
            password='TestPassword123!',
        )

        self.other_resident = User.objects.create_user(
            username='incident_resident_002',
            password='TestPassword123!',
        )

        self.admin = User.objects.create_user(
            username='incident_admin_001',
            password='TestPassword123!',
        )

        UserProfile.objects.create(
            user=self.resident,
            role=UserProfile.Role.RESIDENT,
        )

        UserProfile.objects.create(
            user=self.other_resident,
            role=UserProfile.Role.RESIDENT,
        )

        UserProfile.objects.create(
            user=self.admin,
            role=UserProfile.Role.ADMINISTRATOR,
        )

        self.list_url = reverse('incident-list-create')

        self.incident = Incident.objects.create(
            reporter=self.resident,
            incident_type='FIRE',
            description='Fire reported near a residential building.',
            location='Bignay, Valenzuela City',
        )

    def test_resident_can_submit_incident(self):
        self.client.force_authenticate(user=self.resident)

        response = self.client.post(
            self.list_url,
            {
                'incident_type': 'MEDICAL',
                'description': 'A person needs medical assistance.',
                'location': 'Bignay, Valenzuela City',
                'latitude': '14.700000',
                'longitude': '120.980000',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['reporter'], self.resident.username)
        self.assertEqual(response.data['status'], 'SUBMITTED')

        self.assertTrue(
            Incident.objects.filter(
                reporter=self.resident,
                incident_type='MEDICAL',
            ).exists()
        )

    def test_resident_can_only_view_own_incidents(self):
        self.client.force_authenticate(user=self.resident)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_resident_cannot_view_another_residents_incident(self):
        self.client.force_authenticate(user=self.other_resident)

        detail_url = reverse(
            'incident-detail',
            kwargs={'pk': str(self.incident.pk)},
        )

        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_administrator_can_view_all_incidents(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_administrator_can_update_incident_status(self):
        self.client.force_authenticate(user=self.admin)

        status_url = reverse(
            'incident-status-update',
            kwargs={'pk': str(self.incident.pk)},
        )

        response = self.client.patch(
            status_url,
            {'status': 'VERIFIED'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.incident.refresh_from_db()
        self.assertEqual(self.incident.status, 'VERIFIED')

    def test_cancellation_requires_a_reason(self):
        self.client.force_authenticate(user=self.admin)

        status_url = reverse(
            'incident-status-update',
            kwargs={'pk': str(self.incident.pk)},
        )

        response = self.client.patch(
            status_url,
            {'status': 'CANCELLED'},
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_administrator_can_cancel_with_a_reason(self):
        self.client.force_authenticate(user=self.admin)

        status_url = reverse(
            'incident-status-update',
            kwargs={'pk': str(self.incident.pk)},
        )

        response = self.client.patch(
            status_url,
            {
                'status': 'CANCELLED',
                'cancellation_reason': 'Duplicate incident report.',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.incident.refresh_from_db()
        self.assertEqual(self.incident.status, 'CANCELLED')
        self.assertEqual(
            self.incident.cancellation_reason,
            'Duplicate incident report.',
        )

    def test_resident_cannot_update_incident_status(self):
        self.client.force_authenticate(user=self.resident)

        status_url = reverse(
            'incident-status-update',
            kwargs={'pk': str(self.incident.pk)},
        )

        response = self.client.patch(
            status_url,
            {'status': 'VERIFIED'},
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
