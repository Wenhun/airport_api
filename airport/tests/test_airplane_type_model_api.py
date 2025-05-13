from django.test import TestCase
from django.urls import reverse

from airport.models import AirplaneType
from airport.serializers import AirplaneTypeSerializer

import airport.tests.base_tests as base_tests


URL = reverse("airport:airplane-type-list")
MODEL = AirplaneType


def payload(**params: dict) -> dict:
    defaults = {
        "name": "Test Airplane_type",
    }
    defaults.update(params)

    return defaults


def detail_url(id: int) -> str:
    return reverse("airport:airplane-type-detail", args=[id])


class UnauthenticatedAirplaneTypeApiTests(
    TestCase, base_tests.BaseUnauthenticatedModelApiTests
):
    url = URL


class AuthenticatedAirplaneTypeApiTests(
    TestCase, base_tests.BaseAuthenticatedModelApiTests
):
    api_model = MODEL
    list_serializer = AirplaneTypeSerializer
    detail_serializer = AirplaneTypeSerializer
    url = URL

    def setUp(self) -> None:
        base_tests.BaseAuthenticatedModelApiTests.setUp(self)

    def test_list_model(self, **kwargs) -> None:
        super().test_list_model(
            object_1=payload(), object_2=payload(name="Test Airplane_type 2")
        )

    def test_filter_objects(self) -> None:
        super().test_filter_objects(
            object_1=payload(name="Type 1"),
            object_2=payload(name="Type 2"),
            object_3=payload(name="Test 3"),
            filter={"name": "Type"},
        )

    def test_retrieve_model_detail(self, **kwargs) -> None:
        type = AirplaneType.objects.create(**payload())
        super().test_retrieve_model_detail(
            object=type,
            detail_url=detail_url(type.id),
        )

    def test_create_object_forbidden(self, **kwargs) -> None:
        super().test_create_object_forbidden(
            payload={
                "name": "Test 1",
            }
        )


class AdminAirplaneTypeApiTests(TestCase,
                                base_tests.BaseAdminModelApiTests):
    api_model = MODEL
    url = URL

    def setUp(self) -> None:
        self.payload = payload()
        base_tests.BaseAdminModelApiTests.setUp(self)

    def test_create_object_with_one_to_many_relation(self, **kwargs) -> None:
        self.skipTest("Test skipped: model haven't one to many relationships")
        super().test_create_object_with_one_to_many_relation()
