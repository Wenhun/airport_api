from django.shortcuts import render

import airport.models as models
import airport.serializers as serializers

from rest_framework import viewsets

from rest_framework.serializers import ModelSerializer

from django.db.models import Prefetch

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from rest_framework.request import Request
from rest_framework.response import Response

from django.db.models.query import QuerySet
from airport.permissions import IsAdminOrIfAuthenticatedReadOnly
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action


class QueryParamUtils:
    @staticmethod
    def _params_to_ints(qs: str) -> list[int]:
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    @staticmethod
    def _params_to_strs(qs: str) -> list[str]:
        """Converts a list of string IDs to a list of strings"""
        from urllib.parse import unquote

        return [unquote(str_id.strip()) for str_id in qs.split(",")]
    

class ImageUploadMixin:
    @action(
    methods=["POST"],
    detail=True,
    url_path="upload-image",
    permission_classes=(IsAdminUser,)
    )
    def upload_image(self, request: Request, pk: int=None) -> Response:
        """Endpoint for uploading an image to a specific object"""

        from rest_framework import status

        obj = self.get_object()
        serializer = self.get_serializer(obj, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CountryViewSet(viewsets.ModelViewSet):
    """ViewSet for the Country model."""

    queryset = models.Country.objects.all()
    serializer_class = serializers.CountrySerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self) -> QuerySet:
        """Retrieve the country with filters"""
        name = self.request.query_params.get("name")

        queryset = self.queryset

        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "name",
                type=OpenApiTypes.STR,
                description="Filter by country name (ex. ?name='USA')",
            ),
        ]
    )
    def list(self, request: Request, *args, **kwargs) -> Response:
        return super().list(request, *args, **kwargs)


class CityViewSet(viewsets.ModelViewSet, QueryParamUtils):
    """ViewSet for the City model."""

    queryset = models.City.objects.select_related("country")
    serializer_class = serializers.CitySerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self) -> ModelSerializer:
        """Return the appropriate serializer class based on the request."""

        if self.action == "list":
            return serializers.CityListSerializer

        if self.action == "retrieve":
            return serializers.CityDetailSerializer

        return super().get_serializer_class()

    def get_queryset(self) -> QuerySet:
        """Retrieve the city with filters"""
        name = self.request.query_params.get("name")
        country = self.request.query_params.get("country")

        queryset = self.queryset

        if name:
            queryset = queryset.filter(name__icontains=name)

        if country:
            countries_ids = self._params_to_ints(country)
            queryset = queryset.filter(country__id__in=countries_ids)

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "name",
                type=OpenApiTypes.STR,
                description="Filter by city name (ex. ?name='New York')",
            ),
            OpenApiParameter(
                "country",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by country id (ex. ?country=1,2)",
            ),
        ]
    )
    def list(self, request: Request, *args, **kwargs) -> Response:
        return super().list(request, *args, **kwargs)


class AirportViewSet(viewsets.ModelViewSet, QueryParamUtils):
    """ViewSet for the Airport model."""

    queryset = models.Airport.objects.select_related("closest_big_city")
    serializer_class = serializers.AirportSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self) -> ModelSerializer:
        """Return the appropriate serializer class based on the request."""

        if self.action == "list":
            return serializers.AirportListSerializer

        if self.action == "retrieve":
            return serializers.AirportDetailSerializer

        return super().get_serializer_class()

    def get_queryset(self) -> QuerySet:
        """Retrieve the airport with filters"""
        code = self.request.query_params.get("code")
        name = self.request.query_params.get("name")
        closest_big_city = self.request.query_params.get("closest_big_city")

        queryset = self.queryset

        if code:
            queryset = queryset.filter(code__iexact=code)

        if name:
            queryset = queryset.filter(name__icontains=name)

        if closest_big_city:
            closest_big_cities_ids = self._params_to_ints(closest_big_city)
            queryset = queryset.filter(closest_big_city__id__in=closest_big_cities_ids)

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "code",
                type=OpenApiTypes.STR,
                description="Filter by airport code (ex. ?code='JFK')",
            ),
            OpenApiParameter(
                "name",
                type=OpenApiTypes.STR,
                description="Filter by airport name (ex. ?name='International Airport')",
            ),
            OpenApiParameter(
                "closest_big_city",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by closest_big_city id (ex. ?closest_big_city=1,2)",
            ),
        ]
    )
    def list(self, request: Request, *args, **kwargs) -> Response:
        return super().list(request, *args, **kwargs)


class RouteViewSet(viewsets.ModelViewSet, QueryParamUtils):
    """ViewSet for the Route model."""

    queryset = models.Route.objects.select_related(
        "source",
        "destination",
        "source__closest_big_city",
        "destination__closest_big_city")
    serializer_class = serializers.RouteSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self) -> ModelSerializer:
        """Return the appropriate serializer class based on the request."""

        if self.action == "list":
            return serializers.RouteListSerializer

        if self.action == "retrieve":
            return serializers.RouteDetailSerializer

        return super().get_serializer_class()

    def get_queryset(self) -> QuerySet:
        """Retrieve the route with filters"""
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")
        distance = self.request.query_params.get("distance")

        queryset = self.queryset

        if source:
            sources_ids = self._params_to_strs(source)
            print(sources_ids)
            queryset = queryset.filter(source_id__in=sources_ids)
        if destination:
            destinations_ids = self._params_to_strs(destination)
            queryset = queryset.filter(destination_id__in=destinations_ids)
        if distance:
            queryset = queryset.filter(distance=distance)

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "source",
                type={"type": "list", "items": {"type": "string"}},
                description="Filter by source id (ex. ?source=JFK,ORD)",
            ),
            OpenApiParameter(
                "destination",
                type={"type": "list", "items": {"type": "string"}},
                description="Filter by destination id (ex. ?destination=LAX,ORD)",
            ),
            OpenApiParameter(
                "distance",
                type=OpenApiTypes.FLOAT,
                description="Filter by route distance (ex. ?distance=500)",
            ),
        ]
    )
    def list(self, request: Request, *args, **kwargs) -> Response:
        return super().list(request, *args, **kwargs)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for the AirplaneType model."""

    queryset = models.AirplaneType.objects.all()
    serializer_class = serializers.AirplaneTypeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self) -> QuerySet:
        """Retrieve the airplane type with filters"""
        name = self.request.query_params.get("name")

        queryset = self.queryset

        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "name",
                type=OpenApiTypes.STR,
                description="Filter by airplane type name (ex. ?name='Regional')",
            ),
        ]
    )
    def list(self, request: Request, *args, **kwargs) -> Response:
        return super().list(request, *args, **kwargs)


class AirplaneViewSet(viewsets.ModelViewSet, QueryParamUtils, ImageUploadMixin):
    """ViewSet for the Airplane model."""

    queryset = models.Airplane.objects.select_related("airplane_type")
    serializer_class = serializers.AirplaneSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self) -> ModelSerializer:
        """Return the appropriate serializer class based on the request."""

        if self.action == "list":
            return serializers.AirplaneListSerializer

        if self.action == "retrieve":
            return serializers.AirplaneDetailSerializer

        if self.action == "upload_image":
            return serializers.AirplaneImageSerializer

        return super().get_serializer_class()

    def get_queryset(self) -> QuerySet:
        """Retrieve the airplane with filters"""
        name = self.request.query_params.get("name")
        airplane_type = self.request.query_params.get("airplane_type")
        rows = self.request.query_params.get("rows")
        seats_in_row = self.request.query_params.get("seats_in_row")

        queryset = self.queryset

        if name:
            queryset = queryset.filter(name__icontains=name)

        if airplane_type:
            airplane_types_ids = self._params_to_ints(airplane_type)
            queryset = queryset.filter(airplane_type__id__in=airplane_types_ids)

        if rows:
            queryset = queryset.filter(rows=rows)

        if seats_in_row:
            queryset = queryset.filter(seats_in_row=seats_in_row)

        return queryset.distinct()
    
    @extend_schema(
        parameters=[
            OpenApiParameter(
                "name",
                type=OpenApiTypes.STR,
                description="Filter by airplane name (ex. ?airplane='A330')",
            ),
            OpenApiParameter(
                "airplane_type",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by airplane_type id (ex. ?airplane_type=1,2)",
            ),
            OpenApiParameter(
                "rows",
                type=OpenApiTypes.INT,
                description="Filter by airplane rows (ex. ?rows=1)",
            ),
            OpenApiParameter(
                "seats_in_row",
                type=OpenApiTypes.INT,
                description="Filter by airplane seats_in_row (ex. ?seats_in_row=1)",
            ),
        ]
    )
    def list(self, request: Request, *args, **kwargs) -> Response:
        return super().list(request, *args, **kwargs)


class FlightViewSet(viewsets.ModelViewSet, QueryParamUtils):
    """ViewSet for the Flight model."""

    queryset = models.Flight.objects.select_related(
        "airplane__airplane_type",
        "route",
        "route__source",
        "route__source__closest_big_city",
        "route__destination",
        "route__destination__closest_big_city",
    ).prefetch_related(
        Prefetch("crew", queryset=models.Crew.objects.select_related("position")))
    serializer_class = serializers.FlightSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self) -> ModelSerializer:
        """Return the appropriate serializer class based on the request."""

        if self.action == "list":
            return serializers.FlightListSerializer

        if self.action == "retrieve":
            return serializers.FlightDetailSerializer

        return super().get_serializer_class()

    def get_queryset(self) -> QuerySet:
        """Retrieve the flight with filters"""
        flight_number = self.request.query_params.get("flight_number")
        airplane = self.request.query_params.get("airplane")
        route = self.request.query_params.get("route")
        departure_time = self.request.query_params.get("departure_time")
        arrival_time = self.request.query_params.get("arrival_time")

        queryset = self.queryset

        if flight_number:
            queryset = queryset.filter(flight_number__iexact=flight_number)

        if airplane:
            airplanes_ids = self._params_to_ints(airplane)
            queryset = queryset.filter(airplane__id__in=airplanes_ids)

        if route:
            routes_ids = self._params_to_ints(route)
            queryset = queryset.filter(route__id__in=routes_ids)

        if departure_time:
            queryset = queryset.filter(departure_time=departure_time)

        if arrival_time:
            queryset = queryset.filter(arrival_time=arrival_time)

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "flight_number",
                type=OpenApiTypes.STR,
                description="Filter by flight number (ex. ?flight_number='AA123')",
            ),
            OpenApiParameter(
                "airplane",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by airplane id (ex. ?airplane=1,2)",
            ),
            OpenApiParameter(
                "route",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by route id (ex. ?route=1,2)",
            ),
            OpenApiParameter(
                "departure_time",
                type=OpenApiTypes.DATETIME,
                description="Filter by departure time (ex. ?departure_time=2023-10-01T12:00:00Z)",
            ),
            OpenApiParameter(
                "arrival_time",
                type=OpenApiTypes.DATETIME,
                description="Filter by arrival time (ex. ?arrival_time=2023-10-01T14:00:00Z)",
            ),
        ]
    )
    def list(self, request: Request, *args, **kwargs) -> Response:
        return super().list(request, *args, **kwargs)


class PositionViewSet(viewsets.ModelViewSet):
    """ViewSet for the Position model."""

    queryset = models.Position.objects.all()
    serializer_class = serializers.PositionSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self) -> QuerySet:
        """Retrieve the position with filters"""
        name = self.request.query_params.get("name")

        queryset = self.queryset

        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "name",
                type=OpenApiTypes.STR,
                description="Filter by position name (ex. ?name='Pilot')",
            ),
        ]
    )
    def list(self, request: Request, *args, **kwargs) -> Response:
        return super().list(request, *args, **kwargs)


class CrewViewSet(viewsets.ModelViewSet, QueryParamUtils, ImageUploadMixin):
    """ViewSet for the Crew model."""

    queryset = models.Crew.objects.select_related("position")
    serializer_class = serializers.CrewSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self) -> ModelSerializer:
        """Return the appropriate serializer class based on the request."""

        if self.action == "list":
            return serializers.CrewListSerializer

        if self.action == "retrieve":
            return serializers.CrewDetailSerializer

        if self.action == "upload_image":
            return serializers.CrewImageSerializer

        return super().get_serializer_class()

    def get_queryset(self) -> QuerySet:
        """Retrieve the crew with filters"""
        first_name = self.request.query_params.get("first_name")
        last_name = self.request.query_params.get("last_name")
        position = self.request.query_params.get("position")

        queryset = self.queryset

        if first_name:
            queryset = queryset.filter(first_name__icontains=first_name)

        if last_name:
            queryset = queryset.filter(last_name__icontains=last_name)

        if position:
            positions_ids = self._params_to_ints(position)
            queryset = queryset.filter(position__id__in=positions_ids)

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "first_name",
                type=OpenApiTypes.STR,
                description="Filter by crew first name (ex. ?first_name='John')",
            ),
            OpenApiParameter(
                "last_name",
                type=OpenApiTypes.STR,
                description="Filter by crew last name (ex. ?last_name='Doe')",
            ),
            OpenApiParameter(
                "position",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by position id (ex. ?position=1,2)",
            ),
        ]
    )
    def list(self, request: Request, *args, **kwargs) -> Response:
        return super().list(request, *args, **kwargs)


class OrderViewSet(viewsets.ModelViewSet, QueryParamUtils):
    """ViewSet for the Order model."""

    queryset = models.Order.objects.select_related("user")
    serializer_class = serializers.OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self) -> QuerySet:
        """Retrieve the order with filters"""
        user = self.request.query_params.get("user")

        queryset = self.queryset

        if user:
            queryset = queryset.filter(user__id=user)

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "user",
                type=OpenApiTypes.INT,
                description="Filter by user id (ex. ?user=1)",
            ),
        ]
    )
    def list(self, request: Request, *args, **kwargs) -> Response:
        return super().list(request, *args, **kwargs)


class TicketViewSet(viewsets.ModelViewSet, QueryParamUtils):
    """ViewSet for the Token model."""

    queryset = models.Ticket.objects.select_related("flight", "order")
    serializer_class = serializers.TicketSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self) -> ModelSerializer:
        """Return the appropriate serializer class based on the request."""

        if self.action == "list":
            return serializers.TicketListSerializer
        if self.action == "retrieve":
            return serializers.TicketDetailSerializer

        return super().get_serializer_class()

    def get_queryset(self) -> QuerySet:
        """Retrieve the ticket with filters"""
        flight = self.request.query_params.get("flight")
        order = self.request.query_params.get("order")
        row = self.request.query_params.get("row")
        seat = self.request.query_params.get("seat")

        queryset = self.queryset

        if flight:
            flights_ids = self._params_to_ints(flight)
            queryset = queryset.filter(flight__id__in=flights_ids)

        if order:
            orders_ids = self._params_to_ints(order)
            queryset = queryset.filter(order__id__in=orders_ids)

        if row:
            queryset = queryset.filter(row=row)

        if seat:
            queryset = queryset.filter(seat=seat)

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "flight",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by flight id (ex. ?flight=1,2)",
            ),
            OpenApiParameter(
                "order",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by order id (ex. ?order=1,2)",
            ),
            OpenApiParameter(
                "row",
                type=OpenApiTypes.INT,
                description="Filter by row number (ex. ?row=1)",
            ),
            OpenApiParameter(
                "seat",
                type=OpenApiTypes.INT,
                description="Filter by seat number (ex. ?seat=1)",
            ),
        ]
    )
    def list(self, request: Request, *args, **kwargs) -> Response:
        return super().list(request, *args, **kwargs)
