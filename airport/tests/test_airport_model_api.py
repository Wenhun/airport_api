from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


class UnauthenticatedAirportApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self) -> None:
        res = self.client.get(reverse("airport:airplane-list"))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
