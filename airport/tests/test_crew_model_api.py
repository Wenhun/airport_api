from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from airport.models import Crew, Position
from airport.serializers import CrewListSerializer, CrewDetailSerializer

import airport.tests.base_tests as base_tests


URL = reverse("airport:crew-list")
MODEL = Crew


def payload(**params: dict) -> dict:
    defaults = {
        "first_name": "Test First Name",
        "last_name": "Test Last Name",
        "position": Position.objects.get_or_create(name="Test Position")[0],
    }
    defaults.update(params)

    return defaults


def detail_url(id: int) -> str:
    return reverse("airport:crew-detail", args=[id])


class UnauthenticatedCrewApiTests(
    TestCase, base_tests.BaseUnauthenticatedModelApiTests
):
    url = URL


class AuthenticatedCrewApiTests(TestCase,
                                base_tests.BaseAuthenticatedModelApiTests):
    api_model = MODEL
    list_serializer = CrewListSerializer
    detail_serializer = CrewDetailSerializer
    url = URL

    def setUp(self) -> None:
        base_tests.BaseAuthenticatedModelApiTests.setUp(self)

    def test_list_model(self, **kwargs) -> None:
        Crew.objects.create(**payload())
        Crew.objects.create(**payload())
        res = self.client.get(URL)

        crew = Crew.objects.order_by("id")
        serializer = CrewListSerializer(crew, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_objects(self) -> None:
        super().test_filter_objects(
            object_1=payload(last_name="Last Name 1"),
            object_2=payload(last_name="Last Name 2"),
            object_3=payload(last_name="Test 3"),
            filter={"last_name": "Last"},
        )

    def test_filter_by_county(self) -> None:
        position_1 = Position.objects.create(name="TST_1")
        position_2 = Position.objects.create(name="TST_2")
        super().test_filter_objects(
            object_1=payload(position=position_1),
            object_2=payload(position=position_1),
            object_3=payload(position=position_2),
            filter={"position": position_1.id},
        )

    def test_retrieve_model_detail(self, **kwargs) -> None:
        crew = Crew.objects.create(**payload())
        super().test_retrieve_model_detail(
            object=crew,
            detail_url=detail_url(crew.id),
        )

    def test_create_object_forbidden(self, **kwargs) -> None:
        super().test_create_object_forbidden(
            payload={
                "first_name": "Test First Name",
                "last_name": "Test Last Name",
                "position": payload()["position"].id,
            }
        )


class AdminCrewApiTests(TestCase, base_tests.BaseAdminModelApiTests):
    api_model = MODEL
    url = URL

    def setUp(self) -> None:
        self.test_filed = payload()["position"]
        self.payload = {
            "first_name": "Test First Name",
            "last_name": "Test Last Name",
            "position": self.test_filed.id,
        }
        base_tests.BaseAdminModelApiTests.setUp(self)

    def test_create_object_with_one_to_many_relation(self, **kwargs) -> None:
        super().test_create_object_with_one_to_many_relation(field="position")
