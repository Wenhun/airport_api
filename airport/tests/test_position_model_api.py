from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from airport.models import Position
from airport.serializers import PositionSerializer

import airport.tests.base_tests as base_tests


URL = reverse("airport:position-list")
MODEL = Position


def payload(**params: dict) -> dict:
    defaults = {
        "name": "Test Position",
    }
    defaults.update(params)

    return defaults


def detail_url(id: int) -> str:
    return reverse("airport:position-detail", args=[id])


class UnauthenticatedPositionApiTests(
    TestCase, base_tests.BaseUnauthenticatedModelApiTests
):
    url = URL


class AuthenticatedPositionApiTests(
    TestCase, base_tests.BaseAuthenticatedModelApiTests
):
    api_model = MODEL
    list_serializer = PositionSerializer
    detail_serializer = PositionSerializer
    url = URL

    def setUp(self) -> None:
        base_tests.BaseAuthenticatedModelApiTests.setUp(self)

    def test_list_model(self, **kwargs) -> None:
        Position.objects.create(name="Test 1")
        Position.objects.create(name="Test 2")
        res = self.client.get(URL)

        positions = Position.objects.order_by("id")
        serializer = PositionSerializer(positions, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_objects(self) -> None:
        super().test_filter_objects(
            object_1=payload(name="Position 1"),
            object_2=payload(name="Position 2"),
            object_3=payload(name="Test 3"),
            filter={"name": "Position"},
        )

    def test_retrieve_model_detail(self, **kwargs) -> None:
        type = Position.objects.create(**payload())
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


class AdminPositionApiTests(TestCase, base_tests.BaseAdminModelApiTests):
    api_model = MODEL
    url = URL

    def setUp(self) -> None:
        self.payload = payload()
        base_tests.BaseAdminModelApiTests.setUp(self)

    def test_create_object_with_one_to_many_relation(self, **kwargs) -> None:
        self.skipTest("Test skipped: model haven't one to many relationships")
        super().test_create_object_with_one_to_many_relation()
