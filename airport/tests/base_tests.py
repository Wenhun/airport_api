from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.serializers import Serializer

from django.contrib.auth import get_user_model
from django.db.models import Model


__names: list = []


def auto_feel_name(base_name: str = "TS") -> str:
    if __names:
        if base_name in __names:
            base_name = base_name + str(len(__names))

    __names.append(base_name)

    return base_name


class BaseUnauthenticatedModelApiTests:
    url: str = None

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self) -> None:
        if not self.url:
            raise ValueError(
                "URL must be provided for the test_auth_required method. "
                f"From class: '{self.__class__.__name__}'."
            )

        res = self.client.get(self.url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class BaseAuthenticatedModelApiTests:
    api_model: Model
    list_serializer: Serializer
    detail_serializer: Serializer
    url: str

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test",
            "test_pass",
        )
        self.client.force_authenticate(self.user)

    def test_list_model(self, **kwargs) -> None:
        if "object_1" not in kwargs or "object_2" not in kwargs:
            raise ValueError(
                "Two objects must be provided for the test_list_model method. "
                f"Test Model: {self.api_model} "
                f"From class: '{self.__class__.__name__}'."
            )

        self.api_model.objects.create(**kwargs["object_1"])
        self.api_model.objects.create(**kwargs["object_2"])
        res = self.client.get(self.url)

        objects = self.api_model.objects.order_by("-pk")
        serializer = self.list_serializer(objects, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_objects(self, **kwargs) -> None:
        if not kwargs:
            self.skipTest(
                "This test must be overridden in a subclass with specific "
                "arguments."
            )

        if (
            "object_1" not in kwargs
            or "object_2" not in kwargs
            or "object_3" not in kwargs
        ):
            raise ValueError(
                "Three objects must be provided for the test_filter_objects "
                "method. "
                f"Test Model: {self.api_model} "
                f"From class: '{self.__class__.__name__}'."
            )

        if "filter" not in kwargs:
            raise ValueError(
                "Filter must be provided for the test_filter_objects method. "
                f"Test Model: {self.api_model} "
                f"From class: '{self.__class__.__name__}'."
            )

        object_1 = self.api_model.objects.create(**kwargs["object_1"])
        object_2 = self.api_model.objects.create(**kwargs["object_2"])
        object_3 = self.api_model.objects.create(**kwargs["object_3"])

        res = self.client.get(self.url, kwargs["filter"])

        serializer_1 = self.list_serializer(object_1)
        serializer_2 = self.list_serializer(object_2)
        serializer_3 = self.list_serializer(object_3)

        self.assertIn(serializer_1.data, res.data["results"])
        self.assertIn(serializer_2.data, res.data["results"])
        self.assertNotIn(serializer_3.data, res.data["results"])

    def test_retrieve_model_detail(self, **kwargs) -> None:
        if "object" not in kwargs:
            raise ValueError(
                "Object must be provided for the test_retrieve_model_detail "
                "method."
                f"Test Model: {self.api_model} "
                f"From class: '{self.__class__.__name__}'."
            )

        if "detail_url" not in kwargs:
            raise ValueError(
                "Detail URL must be provided for test_retrieve_model_detail "
                "method."
                f"Test Model: {self.api_model} "
                f"From class: '{self.__class__.__name__}'."
            )

        url = kwargs["detail_url"]
        res = self.client.get(url)

        serializer = self.detail_serializer(kwargs["object"])
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_object_forbidden(self, **kwargs) -> None:
        if "payload" not in kwargs:
            raise ValueError(
                "Payload must be provided for test_create_object_forbidden "
                "method. "
                f"Test Model: {self.api_model} "
                f"From class: '{self.__class__.__name__}'."
            )

        res = self.client.post(self.url, kwargs["payload"])
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class BaseAdminModelApiTests:
    api_model: Model = None
    url: str = None
    test_filed: Model = None
    payload: dict = None

    def __check_create_object(self, payload: dict) -> Model:
        res = self.client.post(self.url, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        return res

    def setUp(self) -> None:
        self.client = APIClient()
        user = get_user_model().objects.create_user(
            "admin@admin.com", "test_pass", is_staff=True
        )
        self.client.force_authenticate(user)

    def test_create_object_without_parameters(self) -> None:
        """Test creating an object without any parameters.
        All fields with relationship will be skipped.
        """
        if not self.payload:
            raise ValueError(
                "Payload must be provided for the "
                "test_create_object_without_parameters method. "
                f"Test Model: {self.api_model} "
                f"From class: '{self.__class__.__name__}'."
            )

        res = self.__check_create_object(self.payload)

        obj = self.api_model.objects.get(pk=res.data["id"])
        for key in self.payload.keys():
            field = self.api_model._meta.get_field(key)
            if field.is_relation and isinstance(self.payload[key], int):
                continue
            self.assertEqual(self.payload[key], getattr(obj, key))

    def test_create_object_with_one_to_many_relation(self, **kwargs) -> None:
        if "field" not in kwargs:
            raise ValueError(
                "Field must be provided for the "
                "test_create_object_with_one_to_many_relationship method. "
                f"Test Model: {self.api_model} "
                f"From class: '{self.__class__.__name__}'."
            )

        if not self.payload:
            raise ValueError(
                "Payload must be provided for the "
                "create_object_with_one_to_many_relationship method. "
                f"Test Model: {self.api_model} "
                f"From class: '{self.__class__.__name__}'."
            )

        res = self.__check_create_object(self.payload)

        obj = self.api_model.objects.get(pk=res.data["id"])

        object_required_field = getattr(obj, kwargs["field"])

        self.assertEqual(
            object_required_field,
            self.test_filed,
        )
