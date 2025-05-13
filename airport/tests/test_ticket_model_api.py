from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from airport.models import Ticket, Order, Flight
from airport.serializers import TicketDetailSerializer, TicketListSerializer

from airport.tests.base_tests import (
    BaseAuthenticatedModelApiTests,
    BaseUnauthenticatedModelApiTests,
    BaseAdminModelApiTests,
)

from airport.tests.test_order_model_api import payload as order_payload
from airport.tests.test_flight_model_api import payload as flight_payload


URL = reverse("airport:ticket-list")
MODEL = Ticket


def payload(**params: dict) -> dict:
    order, _ = Order.objects.get_or_create(**order_payload())
    flight, _ = Flight.objects.get_or_create(**flight_payload())
    defaults = {
        "order": order,
        "flight": flight,
        "row": 1,
        "seat": 1,
    }
    defaults.update(params)

    return defaults


def detail_url(id: int) -> str:
    return reverse("airport:ticket-detail", args=[id])


class UnauthenticatedCityApiTests(TestCase, BaseUnauthenticatedModelApiTests):
    url = URL


class AuthenticatedCityApiTests(TestCase, BaseAuthenticatedModelApiTests):
    api_model = MODEL
    list_serializer = TicketListSerializer
    detail_serializer = TicketDetailSerializer
    url = URL

    def setUp(self) -> None:
        BaseAuthenticatedModelApiTests.setUp(self)

    def test_list_model(self, **kwargs) -> None:
        MODEL.objects.create(**payload())
        MODEL.objects.create(**payload(seat=2))
        res = self.client.get(URL)

        tickets = MODEL.objects.order_by("id")
        serializer = TicketListSerializer(tickets, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_objects(self) -> None:
        order_1 = Order.objects.create(**order_payload())
        order_2 = Order.objects.create(**order_payload())
        super().test_filter_objects(
            object_1=payload(order=order_1),
            object_2=payload(seat=2, order=order_1),
            object_3=payload(seat=3, order=order_2),
            filter={"order": order_1.id},
        )

    def test_filter_by_flight(self) -> None:
        flight_1 = Flight.objects.create(**flight_payload())
        flight_2 = Flight.objects.create(**flight_payload())
        super().test_filter_objects(
            object_1=payload(flight=flight_1),
            object_2=payload(seat=2, flight=flight_1),
            object_3=payload(seat=3, flight=flight_2),
            filter={"flight": flight_1.id},
        )

    def test_retrieve_model_detail(self, **kwargs) -> None:
        ticket = Ticket.objects.create(**payload())
        super().test_retrieve_model_detail(
            object=ticket,
            detail_url=detail_url(ticket.id),
        )

    def test_create_object_forbidden(self, **kwargs) -> None:
        super().test_create_object_forbidden(
            payload = {
                "order": payload()["order"].id,
                "flight": payload()["flight"].id,
                "row": 1,
                "seat": 1,
            }
        )


class AdminCityApiTests(TestCase, BaseAdminModelApiTests):
    api_model = MODEL
    url = URL

    def setUp(self) -> None:
        self.test_filed = payload()["order"]
        self.payload = {
            "order": self.test_filed.id,
            "flight": payload()["flight"].id,
            "row": 1,
            "seat": 1,
        }
        BaseAdminModelApiTests.setUp(self)

    def test_create_object_with_one_to_many_relation(self, **kwargs) -> None:
        super().test_create_object_with_one_to_many_relation(field="order")

    def test_create_object_flight(self, **kwargs) -> None:
        self.test_filed = payload()["flight"]
        self.payload = {
            "order": payload()["order"].id,
            "flight": self.test_filed.id,
            "row": 1,
            "seat": 1,
        }
        super().test_create_object_with_one_to_many_relation(field="flight")

    def test_create_ticket_goes_beyond_limitations(self) -> None:
        self.payload = {
            "order": payload()["order"].id,
            "flight": payload()["flight"].id,
            "row": 99,
            "seat": 99,
        }
        res = self.client.post(self.url, self.payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)