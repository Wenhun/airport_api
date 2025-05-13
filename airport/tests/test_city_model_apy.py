from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from airport.models import City, Country
from airport.serializers import CityListSerializer, CityDetailSerializer

from airport.tests.base_tests import (
    BaseAuthenticatedModelApiTests,
    BaseUnauthenticatedModelApiTests,
    BaseAdminModelApiTests,
)


URL = reverse("airport:city-list")
MODEL = City


def payload(**params: dict) -> dict:
    defaults = {
        "name": "Test City",
        "country": Country.objects.get_or_create(name="Test Country")[0],
    }
    defaults.update(params)

    return defaults


def detail_url(id: int) -> str:
    return reverse("airport:city-detail", args=[id])


class UnauthenticatedCityApiTests(TestCase, BaseUnauthenticatedModelApiTests):
    url = URL


class AuthenticatedCityApiTests(TestCase, BaseAuthenticatedModelApiTests):
    api_model = MODEL
    list_serializer = CityListSerializer
    detail_serializer = CityDetailSerializer
    url = URL

    def setUp(self) -> None:
        BaseAuthenticatedModelApiTests.setUp(self)

    def test_list_model(self, **kwargs) -> None:
        City.objects.create(**payload())
        City.objects.create(**payload())
        res = self.client.get(URL)

        cities = City.objects.order_by("id")
        serializer = CityListSerializer(cities, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_objects(self) -> None:
        super().test_filter_objects(
            object_1=payload(name="City 1"),
            object_2=payload(name="City 2"),
            object_3=payload(name="Test 3"),
            filter={"name": "City"},
        )

    def test_filter_by_county(self) -> None:
        country_1 = Country.objects.create(name="TST_1")
        country_2 = Country.objects.create(name="TST_2")
        super().test_filter_objects(
            object_1=payload(name="City 1_1", country=country_1),
            object_2=payload(name="City 2_1", country=country_1),
            object_3=payload(name="City 3_2", country=country_2),
            filter={"country": country_1.id},
        )

    def test_retrieve_model_detail(self, **kwargs) -> None:
        city = City.objects.create(**payload())
        super().test_retrieve_model_detail(
            object=city,
            detail_url=detail_url(city.id),
        )

    def test_create_object_forbidden(self, **kwargs) -> None:
        super().test_create_object_forbidden(
            payload={"name": "city 1", "country": payload()["country"].id}
        )


class AdminCityApiTests(TestCase, BaseAdminModelApiTests):
    api_model = MODEL
    url = URL

    def setUp(self) -> None:
        self.test_filed = payload()["country"]
        self.payload = {"name": "Test City", "country": self.test_filed.id}
        BaseAdminModelApiTests.setUp(self)

    def test_create_object_with_one_to_many_relation(self, **kwargs) -> None:
        super().test_create_object_with_one_to_many_relation(field="country")
