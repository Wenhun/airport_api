import tempfile
import os

from PIL import Image

from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

from django.test import TestCase
from django.urls import reverse

from airport.models import Airplane, AirplaneType
from airport.serializers import (
    AirplaneListSerializer,
    AirplaneDetailSerializer,
)
from airport.tests.base_tests import (
    BaseAuthenticatedModelApiTests,
    BaseUnauthenticatedModelApiTests,
    BaseAdminModelApiTests,
)


URL = reverse("airport:airplane-list")
MODEL = Airplane


def payload(**params: dict) -> dict:
    defaults = {
        "name": "Test Airplane",
        "airplane_type": AirplaneType.objects.get_or_create(
            name="Test Type"
        )[0],
        "rows": 20,
        "seats_in_row": 6,
    }
    defaults.update(params)

    return defaults


def detail_url(id: int) -> str:
    return reverse("airport:airplane-detail", args=[id])


def image_upload_url(airplane_id: int) -> str:
    """Return URL for recipe image upload"""
    return reverse("airport:airplane-upload-image", args=[airplane_id])


class UnauthenticatedAirplaneApiTests(TestCase,
                                      BaseUnauthenticatedModelApiTests):
    url = URL


class AuthenticatedAirplaneApiTests(TestCase, BaseAuthenticatedModelApiTests):
    api_model = MODEL
    list_serializer = AirplaneListSerializer
    detail_serializer = AirplaneDetailSerializer
    url = URL

    def setUp(self) -> None:
        BaseAuthenticatedModelApiTests.setUp(self)

    def test_list_model(self, **kwargs) -> BaseAdminModelApiTests:
        super().test_list_model(object_1=payload(), object_2=payload())

    def test_filter_by_airplane_type(self) -> None:
        airplane_type_1 = AirplaneType.objects.create(name="Type 1")
        airplane_type_2 = AirplaneType.objects.create(name="Type 2")
        super().test_filter_objects(
            object_1=payload(
                name="Airplane 1_1", airplane_type=airplane_type_1
            ),
            object_2=payload(
                name="Airplane 2_1", airplane_type=airplane_type_1
            ),
            object_3=payload(
                name="Airplane 3_2", airplane_type=airplane_type_2
            ),
            filter={"airplane_type": airplane_type_1.id},
        )

    def test_filter_objects(self) -> None:
        super().test_filter_objects(
            object_1=payload(name="Airplane 1"),
            object_2=payload(name="Airplane 2"),
            object_3=payload(name="Test 3"),
            filter={"name": "Airplane"},
        )

    def test_retrieve_model_detail(self, **kwargs) -> None:
        airplane = Airplane.objects.create(**payload())
        super().test_retrieve_model_detail(
            object=airplane,
            detail_url=detail_url(airplane.id),
        )

    def test_create_object_forbidden(self, **kwargs) -> None:
        super().test_create_object_forbidden(
            payload={
                "name": "Airplane 1",
                "airplane_type": AirplaneType.objects.create(
                    name="Test Type"
                ).id,
            }
        )


class AdminAirplaneApiTests(TestCase, BaseAdminModelApiTests):
    api_model = MODEL
    url = URL

    def setUp(self) -> None:
        self.test_filed = AirplaneType.objects.create(name="Test Type")
        self.payload = {
            "name": "Airplane 1",
            "airplane_type": self.test_filed.id,
            "rows": 20,
            "seats_in_row": 6,
        }
        BaseAdminModelApiTests.setUp(self)

    def test_create_object_with_one_to_many_relation(self, **kwargs) -> None:
        super().test_create_object_with_one_to_many_relation(
            field="airplane_type"
        )


class AirplaneImageUploadTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@myproject.com", "password"
        )
        self.client.force_authenticate(self.user)
        self.airplane = Airplane.objects.create(**payload())

    def tearDown(self) -> None:
        self.airplane.image.delete()

    def test_upload_image_to_airplane(self) -> None:
        """Test uploading an image to airplane"""
        url = image_upload_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.airplane.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.airplane.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.airplane.id)
        res = self.client.post(url, {"image": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_airplane_list_should_not_work(self) -> None:
        name = "Airplane Test"
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                URL,
                {
                    "name": name,
                    "airplane_type": payload()["airplane_type"].id,
                    "rows": 20,
                    "seats_in_row": 6,
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        airplane = Airplane.objects.get(name=name)
        self.assertFalse(airplane.image)

    def test_image_url_is_shown_on_airplane_detail(self) -> None:
        url = image_upload_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(detail_url(self.airplane.id))

        self.assertIn("image", res.data)

    def test_image_url_is_shown_on_airplane_list(self) -> None:
        url = image_upload_url(self.airplane.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(URL)

        self.assertIn("image", res.data["results"][0].keys())

    def test_put_airplane_not_allowed(self) -> None:
        put_payload = {
            "name": "Airplane 1",
            "airplane_type": payload()["airplane_type"].id,
            "rows": 20,
            "seats_in_row": 6,
        }

        airplane = Airplane.objects.create(**payload())
        url = detail_url(airplane.id)

        res = self.client.put(url, put_payload)

        self.assertEqual(
            res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_delete_airplane_not_allowed(self) -> None:
        airplane = Airplane.objects.create(**payload())
        url = detail_url(airplane.id)

        res = self.client.delete(url)

        self.assertEqual(
            res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )
