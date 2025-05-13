from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from airport.models import Route, Airport
from airport.serializers import RouteListSerializer, RouteDetailSerializer

import airport.tests.base_tests as base_tests
from airport.tests.test_airport_model_api import payload as airport_payload


URL = reverse("airport:route-list")
MODEL = Route


def payload(**params: dict) -> dict:
    Airport.objects.all().delete()
    source = Airport.objects.create(**(airport_payload(code="TS1")))
    destination = Airport.objects.create(**(airport_payload(code="TS2")))

    defaults = {"source": source, "destination": destination, "distance": 0}
    defaults.update(params)

    return defaults


def detail_url(id: int) -> str:
    return reverse("airport:route-detail", args=[id])


class UnauthenticatedRouteApiTests(
    TestCase, base_tests.BaseUnauthenticatedModelApiTests
):
    url = URL


class AuthenticatedRouteApiTests(TestCase,
                                 base_tests.BaseAuthenticatedModelApiTests):
    api_model = MODEL
    list_serializer = RouteListSerializer
    detail_serializer = RouteDetailSerializer
    url = URL
    airport: Airport

    def setUp(self) -> None:
        base_tests.BaseAuthenticatedModelApiTests.setUp(self)

    def test_list_model(self, **kwargs) -> None:
        Route.objects.create(**payload())
        Route.objects.create(**payload())
        res = self.client.get(URL)

        routes = Route.objects.order_by("id")
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_by_source(self) -> None:
        source_1 = payload()["source"]
        source_2 = payload()["destination"]
        super().test_filter_objects(
            object_1=payload(source=source_1),
            object_2=payload(source=source_1),
            object_3=payload(source=source_2),
            filter={"source": source_1.code},
        )

    def test_filter_by_destination(self) -> None:
        destination_1 = payload()["destination"]
        destination_2 = payload()["source"]
        super().test_filter_objects(
            object_1=payload(destination=destination_1),
            object_2=payload(destination=destination_1),
            object_3=payload(destination=destination_2),
            filter={"destination": destination_1.code},
        )

    def test_retrieve_model_detail(self, **kwargs) -> None:
        route = Route.objects.create(**payload())
        super().test_retrieve_model_detail(
            object=route,
            detail_url=detail_url(route.id),
        )

    def test_create_object_forbidden(self, **kwargs) -> None:
        super().test_create_object_forbidden(
            payload={
                "source": payload()["source"].code,
                "destination": payload()["destination"].code,
                "distance": 0,
            }
        )


class AdminRouteApiTests(TestCase, base_tests.BaseAdminModelApiTests):
    api_model = MODEL
    url = URL

    def setUp(self) -> None:
        self.test_filed = payload()["source"]
        self.payload = {
            "source": self.test_filed.code,
            "destination": payload()["destination"].code,
            "distance": 0,
        }
        base_tests.BaseAdminModelApiTests.setUp(self)

    def test_create_object_without_parameters(self, **kwargs) -> None:
        self.skipTest(
            "Test skipped: model have only one field without relationships")
        super().test_create_object_without_parameters()

    def test_create_object_with_one_to_many_relation(self, **kwargs) -> None:
        self.skipTest(
            "Test skipped: This test override with specific arguments")
        super().test_create_object_with_one_to_many_relation()

    def test_create_route_test_source(self, **kwargs) -> None:
        super().test_create_object_with_one_to_many_relation(field="source")

    def test_create_route_test_destination(self, **kwargs) -> None:
        self.test_filed = payload()["destination"]
        self.payload = {
            "source": payload()["source"].code,
            "destination": self.test_filed.code,
            "distance": 0,
        }
        super().test_create_object_with_one_to_many_relation(
            field="destination")
