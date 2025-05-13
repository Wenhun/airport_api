from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from django.db import models

from airport.models import Order
from airport.serializers import OrderSerializer

from airport.tests.base_tests import (
    BaseAuthenticatedModelApiTests,
    BaseUnauthenticatedModelApiTests,
    BaseAdminModelApiTests
)

URL = reverse("airport:order-list")
MODEL = Order


def payload(**params: dict) -> dict:
    defaults = {
        "created_at": "2025-05-02 09:13:35.961790+00:00",
        "user": get_user_model().objects.get_or_create(
            username="test", defaults={"password": "test_password"}
        )[0],
    }
    defaults.update(params)

    return defaults


class UnauthenticatedOrderApiTests(TestCase,
                                   BaseUnauthenticatedModelApiTests):
    url = URL


class AuthenticatedOrderApiTests(TestCase, BaseAuthenticatedModelApiTests):
    api_model = MODEL
    list_serializer = OrderSerializer
    detail_serializer = OrderSerializer
    url = URL

    def setUp(self) -> None:
        BaseAuthenticatedModelApiTests.setUp(self)

    def test_list_model(self, **kwargs) -> None:
        super().test_list_model(
            object_1=payload(),
            object_2=payload(),
        )

    def test_filter_objects(self) -> None:
        """Filter by User"""
        user_1 = get_user_model().objects.create(
            username="test_1", password="test_password"
        )
        user_2 = get_user_model().objects.create(
            username="test_2", password="test_password"
        )

        super().test_filter_objects(
            object_1=payload(user=user_1),
            object_2=payload(user=user_1),
            object_3=payload(user=user_2),
            filter={"user": user_1.id},
        )

    def test_retrieve_model_detail(self, **kwargs) -> None:
        self.skipTest("Model haven't detail page")
        super().test_retrieve_model_detail()

    def test_create_object_forbidden(self, **kwargs) -> None:
        self.skipTest("Unauthenticated users can create order")


class AdminOrderApiTests(TestCase, BaseAdminModelApiTests):
    api_model = MODEL
    url = URL

    def setUp(self) -> None:
        self.payload = {
            "created_at": "2025-05-02 09:13:35.961790+00:00",
            "user": payload()["user"].id,
        }
        BaseAdminModelApiTests.setUp(self)

    def test_create_object_without_parameters(self) -> None:
        res = self.client.post(self.url, self.payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        obj = self.api_model.objects.get(pk=res.data["id"])
        for key in self.payload.keys():
            field = self.api_model._meta.get_field(key)
            # Only check auto_now_add for DateTimeField
            if isinstance(field, models.DateTimeField) and field.auto_now_add:
                continue
            if field.is_relation and isinstance(self.payload[key], int):
                continue
            self.assertEqual(self.payload[key], getattr(obj, key))

    def test_create_object_with_one_to_many_relation(self, **kwargs) -> None:
        self.skipTest("Test skipped: model haven't one to many relationships")
        super().test_create_object_with_one_to_many_relation()
