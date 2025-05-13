from django.test import TestCase
from django.urls import reverse

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from airport.models import Airport, City
from airport.serializers import AirportDetailSerializer, AirportListSerializer

import airport.tests.base_tests as base_tests
from airport.tests.test_city_model_apy import payload as city_payload


URL = reverse("airport:airport-list")
MODEL = Airport


def payload(**params: dict) -> dict:
    defaults = {
        "code": base_tests.auto_feel_name("TS"),
        "name": "Test Airport",
        "closest_big_city": City.objects.get_or_create(**city_payload())[0],
    }
    defaults.update(params)

    return defaults


def detail_url(id: int) -> str:
    return reverse("airport:airport-detail", args=[id])


class UnauthenticatedAirportApiTests(
    TestCase, base_tests.BaseUnauthenticatedModelApiTests
):
    url = URL


class AuthenticatedAirportApiTests(TestCase,
                                   base_tests.BaseAuthenticatedModelApiTests):
    api_model = MODEL
    list_serializer = AirportListSerializer
    detail_serializer = AirportDetailSerializer
    url = URL

    def setUp(self) -> None:
        base_tests.BaseAuthenticatedModelApiTests.setUp(self)

    def test_list_model(self, **kwargs) -> None:
        super().test_list_model(object_1=payload(), object_2=payload())

    def test_filter_by_city(self) -> None:
        city_1 = City.objects.create(**city_payload())
        city_2 = City.objects.create(**city_payload(name="Test City 2"))
        super().test_filter_objects(
            object_1=payload(closest_big_city=city_1),
            object_2=payload(closest_big_city=city_1),
            object_3=payload(closest_big_city=city_2),
            filter={"closest_big_city": city_1.id},
        )

    def test_filter_by_code(self) -> None:
        airport_1 = self.api_model.objects.create(
            code="TS1", closest_big_city=City.objects.create(**city_payload())
        )
        airport_2 = self.api_model.objects.create(
            code="TS2", closest_big_city=City.objects.create(**city_payload())
        )

        res = self.client.get(self.url, {"code": "TS1"})

        serializer_1 = self.list_serializer(airport_1)
        serializer_2 = self.list_serializer(airport_2)

        self.assertIn(serializer_1.data, res.data["results"])
        self.assertNotIn(serializer_2.data, res.data["results"])

    def test_filter_objects(self) -> None:
        super().test_filter_objects(
            object_1=payload(name="Test Airport 1"),
            object_2=payload(name="Test Airport 2"),
            object_3=payload(name="Airport 3"),
            filter={"name": "Test"},
        )

    def test_retrieve_model_detail(self, **kwargs) -> None:
        airport = Airport.objects.create(**payload())
        super().test_retrieve_model_detail(
            object=airport,
            detail_url=detail_url(airport.code),
        )

    def test_create_object_forbidden(self, **kwargs) -> None:
        super().test_create_object_forbidden(
            payload={
                "code": base_tests.auto_feel_name(),
                "closest_big_city": City.objects.create(**city_payload()).id,
            }
        )


class AdminAirportApiTests(TestCase):
    payload: dict

    def setUp(self) -> None:
        self.client = APIClient()
        user = get_user_model().objects.create_user(
            "admin@admin.com", "test_pass", is_staff=True
        )
        self.client.force_authenticate(user)

        self.payload = {
            "code": "TST",
            "name": "Test Airport",
            "closest_big_city":
                City.objects.get_or_create(**city_payload())[0].id,
        }

    def test_create_object_without_parameters(self) -> None:
        res = self.client.post(URL, self.payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        airport = Airport.objects.get(pk=res.data["code"])
        for key in self.payload.keys():
            field = Airport._meta.get_field(key)
            if field.is_relation and isinstance(self.payload[key], int):
                continue
            self.assertEqual(self.payload[key], getattr(airport, key))

    def test_create_object_with_one_to_many_relation(self, **kwargs) -> None:
        res = self.client.post(URL, self.payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        airport = Airport.objects.get(pk=res.data["code"])

        self.assertEqual(airport.closest_big_city,
                         getattr(airport, "closest_big_city"))
