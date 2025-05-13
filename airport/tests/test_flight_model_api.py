from datetime import datetime
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

from airport.models import Flight, Crew, Route, Airplane, Airport
from airport.serializers import (
    FlightListSerializer,
    FlightDetailSerializer
)

import airport.tests.base_tests as base_tests
from airport.tests.test_airplane_model_api import payload as airplane_payload
from airport.tests.test_airport_model_api import payload as airport_payload
from airport.tests.test_crew_model_api import payload as crew_payload


URL = reverse("airport:flight-list")
MODEL = Flight


def route_payload(**params: dict) -> dict:
    source, _ = Airport.objects.get_or_create(
        defaults=airport_payload(code="TS1"), code="TS1"
    )
    destination, _ = Airport.objects.get_or_create(
        defaults=airport_payload(code="TS2"), code="TS2"
    )

    defaults = {"source": source, "destination": destination, "distance": 0}
    defaults.update(params)

    return defaults


def payload(**params: dict) -> dict:
    defaults = {
        "flight_number": base_tests.auto_feel_name(),
        "route": Route.objects.create(**route_payload()),
        "airplane": Airplane.objects.create(**airplane_payload()),
        "departure_time": "2025-04-25T15:12:10Z",
        "arrival_time": "2025-04-26T15:12:12Z",
    }
    defaults.update(params)

    return defaults


def detail_url(id: int) -> str:
    return reverse("airport:flight-detail", args=[id])


class UnauthenticatedFlightApiTests(
    TestCase, base_tests.BaseUnauthenticatedModelApiTests
):
    url = URL


class AuthenticatedFlightApiTests(TestCase,
                                  base_tests.BaseAuthenticatedModelApiTests):
    api_model = MODEL
    list_serializer = FlightListSerializer
    detail_serializer = FlightDetailSerializer
    url = URL

    def setUp(self) -> None:
        base_tests.BaseAuthenticatedModelApiTests.setUp(self)

    def test_list_model(self, **kwargs) -> None:
        Flight.objects.create(**payload())
        Flight.objects.create(**payload())
        res = self.client.get(URL)

        flights = Flight.objects.order_by("id")
        serializer = FlightListSerializer(flights, many=True)

        # Exclude 'tickets_available' field from the serialized data
        expected_data = [
            {key: value
             for key, value in item.items() if key != "tickets_available"}
            for item in serializer.data
        ]

        # Exclude 'tickets_available' field from the response data
        actual_data = [
            {key: value
             for key, value in item.items() if key != "tickets_available"}
            for item in res.data["results"]
        ]

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(actual_data, expected_data)

    def __assert_filter_results(
        self, filter: dict, payload_1: dict, payload_2: dict
    ) -> None:
        flight_1 = Flight.objects.create(**payload_1)
        flight_2 = Flight.objects.create(**payload_2)
        res = self.client.get(self.url, filter)

        serializer_1 = FlightListSerializer(flight_1)
        serializer_2 = FlightListSerializer(flight_2)

        serializer_1_data = {
            key: value
            for key, value in serializer_1.data.items()
            if key != "tickets_available"
        }
        serializer_2_data = {
            key: value
            for key, value in serializer_2.data.items()
            if key != "tickets_available"
        }

        response_data = [
            {key: value
             for key, value in item.items() if key != "tickets_available"}
            for item in res.data["results"]
        ]

        self.assertIn(serializer_1_data, response_data)
        self.assertNotIn(serializer_2_data, response_data)

    def test_filter_by_flight_number(self) -> None:
        self.__assert_filter_results(
            filter={"flight_number": "TST123"},
            payload_1=payload(flight_number="TST123"),
            payload_2=payload(),
        )

    def test_filter_by_route(self) -> None:
        route_1 = Route.objects.create(**route_payload())
        route_2 = Route.objects.create(**route_payload())
        self.__assert_filter_results(
            filter={"route": f"{route_1.pk}"},
            payload_1=payload(route=route_1),
            payload_2=payload(route=route_2),
        )

    def test_filter_by_airplane(self) -> None:
        airplane_1 = Airplane.objects.create(**airplane_payload())
        airplane_2 = Airplane.objects.create(**airplane_payload())
        self.__assert_filter_results(
            filter={"airplane": f"{airplane_1.pk}"},
            payload_1=payload(airplane=airplane_1),
            payload_2=payload(airplane=airplane_2),
        )

    def test_retrieve_model_detail(self, **kwargs) -> None:
        flight = Flight.objects.create(**payload())
        super().test_retrieve_model_detail(
            object=flight, detail_url=detail_url(flight.id)
        )

    def test_create_object_forbidden(self, **kwargs) -> None:
        super().test_create_object_forbidden(
            payload={
                "flight_number": "TST123",
                "route": payload()["route"].id,
                "airplane": payload()["airplane"].id,
                "departure_time":
                    datetime(2025, 4, 28, 17, 10, 0).isoformat() + "Z",
                "arrival_time":
                    datetime(2025, 4, 28, 18, 0, 0).isoformat() + "Z",
            }
        )


class AdminFlightApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        user = get_user_model().objects.create_user(
            "admin@admin.com", "test_pass", is_staff=True
        )
        self.client.force_authenticate(user)

        self.crew = Crew.objects.create(**crew_payload())
        self.route = Route.objects.create(**route_payload())
        self.airplane = Airplane.objects.create(**airplane_payload())

        self.payload = {
            "flight_number": "TST123",
            "route": self.route.pk,
            "airplane": self.airplane.pk,
            "crew": [self.crew.pk],
            "departure_time": "2025-04-25T15:12:10Z",
            "arrival_time": "2025-04-26T15:12:12Z",
        }

    def test_create_flight_without_relationship(self) -> None:
        res = self.client.post(URL, self.payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        flight = Flight.objects.get(pk=res.data["id"])
        for key in self.payload.keys():
            field = Flight._meta.get_field(key)
            if field.is_relation and isinstance(self.payload[key], int):
                continue
            if field.is_relation and isinstance(self.payload[key], list):
                continue
            if (
                isinstance(self.payload[key], str)
                and "T" in self.payload[key]
                and "Z" in self.payload[key]
            ):
                self.assertEqual(
                    datetime.fromisoformat(
                        self.payload[key].replace("Z", "+00:00")),
                    getattr(flight, key),
                )
            else:
                self.assertEqual(self.payload[key], getattr(flight, key))

    def test_create_flight_with_airplane(self) -> None:
        res = self.client.post(URL, self.payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        flight = Flight.objects.get(pk=res.data["id"])

        airplane = flight.airplane

        self.assertEqual(airplane, self.airplane)

    def test_create_flight_with_route(self) -> None:
        res = self.client.post(URL, self.payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        flight = Flight.objects.get(pk=res.data["id"])

        route = flight.route

        self.assertEqual(route, self.route)

    def test_create_flight_with_crew(self):
        crew_1 = Crew.objects.create(**crew_payload(last_name="TST"))
        crew_2 = Crew.objects.create(**crew_payload(last_name="Test"))

        self.payload.update(crew=[crew_1.pk, crew_2.pk])

        res = self.client.post(URL, self.payload)

        flight = Flight.objects.get(id=res.data["id"])
        crew = flight.crew.all()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn(crew_1, crew)
        self.assertIn(crew_2, crew)
        self.assertEqual(crew.count(), 2)
