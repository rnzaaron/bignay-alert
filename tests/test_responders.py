from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.responders.models import ResponderProfile


class ResponderProfileAPITests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.admin = user_model.objects.create_user(
            username='responder-admin',
            password='test-password',
            is_staff=True,
        )
        self.responder_user = user_model.objects.create_user(
            username='responder-one',
            password='test-password',
        )
        self.profile_data = {
            'user': str(self.responder_user.pk),
            'specialization': ResponderProfile.Specialization.MEDICAL,
            'contact_number': '555-0100',
            'assigned_area': 'North zone',
        }
        self.list_url = '/api/responders/'
        self.availability_url = '/api/responders/me/availability/'

    def test_admin_can_create_retrieve_and_update_responder(self):
        self.client.force_authenticate(user=self.admin)

        create_response = self.client.post(
            self.list_url,
            self.profile_data,
            format='json',
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        profile_id = create_response.data['id']
        self.assertEqual(create_response.data['availability'], 'OFFLINE')

        list_response = self.client.get(self.list_url)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data), 1)

        detail_url = f'{self.list_url}{profile_id}/'
        detail_response = self.client.get(detail_url)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.data['username'], 'responder-one')

        update_response = self.client.patch(
            detail_url,
            {'assigned_area': 'South zone'},
            format='json',
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data['assigned_area'], 'South zone')

    def test_responder_can_update_only_own_availability(self):
        profile = ResponderProfile.objects.create(
            user=self.responder_user,
            specialization=ResponderProfile.Specialization.GENERAL,
            contact_number='555-0101',
        )
        self.client.force_authenticate(user=self.responder_user)

        response = self.client.patch(
            self.availability_url,
            {'availability': ResponderProfile.Availability.RESPONDING},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        profile.refresh_from_db()
        self.assertEqual(
            profile.availability,
            ResponderProfile.Availability.RESPONDING,
        )

        update_profile_response = self.client.patch(
            f'{self.list_url}{profile.pk}/',
            {'assigned_area': 'Unauthorized change'},
            format='json',
        )
        self.assertEqual(
            update_profile_response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_invalid_availability_is_rejected(self):
        ResponderProfile.objects.create(
            user=self.responder_user,
            specialization=ResponderProfile.Specialization.GENERAL,
            contact_number='555-0101',
        )
        self.client.force_authenticate(user=self.responder_user)

        response = self.client.patch(
            self.availability_url,
            {'availability': 'ON_CALL'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
