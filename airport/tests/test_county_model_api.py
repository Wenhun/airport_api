from django.test import TestCase
from django.urls import reverse

from airport.models import Country
from airport.serializers import CountrySerializer

from airport.tests.base_tests import (
    BaseAuthenticatedModelApiTests,
    BaseUnauthenticatedModelApiTests,
    BaseAdminModelApiTests
)

URL = reverse("airport:country-list")
MODEL = Country


def payload(**params: dict) -> dict:
    defaults = {
        "name": "Test Country",
    }
    defaults.update(params)

    return defaults


def detail_url(id: int) -> str:
    return reverse("airport:country-detail", args=[id])


class UnauthenticatedCountryApiTests(TestCase,
                                     BaseUnauthenticatedModelApiTests):
    url = URL


class AuthenticatedCountryApiTests(TestCase, BaseAuthenticatedModelApiTests):
    api_model = MODEL
    list_serializer = CountrySerializer
    detail_serializer = CountrySerializer
    url = URL

    def setUp(self) -> None:
        BaseAuthenticatedModelApiTests.setUp(self)

    def test_list_model(self, **kwargs) -> None:
        super().test_list_model(
            object_1=payload(name="Test 1"),
            object_2=payload(name="Test 2"),
        )

    def test_filter_objects(self) -> None:
        super().test_filter_objects(
            object_1=payload(name="Country 1"),
            object_2=payload(name="Country 2"),
            object_3=payload(name="Test 3"),
            filter={"name": "Country"},
        )

    def test_retrieve_model_detail(self, **kwargs) -> None:
        county = Country.objects.create(**payload())
        super().test_retrieve_model_detail(
            object=county,
            detail_url=detail_url(county.id),
        )

    def test_create_object_forbidden(self, **kwargs) -> None:
        super().test_create_object_forbidden(
            payload={
                "name": "Test 1",
            }
        )


class AdminCountyApiTests(TestCase, BaseAdminModelApiTests):
    api_model = MODEL
    url = URL

    def setUp(self) -> None:
        self.payload = payload()
        BaseAdminModelApiTests.setUp(self)

    def test_create_object_with_one_to_many_relation(self, **kwargs) -> None:
        self.skipTest("Test skipped: model haven't one to many relationships")
        super().test_create_object_with_one_to_many_relation()
