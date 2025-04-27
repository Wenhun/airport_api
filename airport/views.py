from django.shortcuts import render

import airport.models as models
import airport.serializers as serializers

from rest_framework import viewsets

from rest_framework.serializers import ModelSerializer


class CountryViewSet(viewsets.ModelViewSet):
    """ViewSet for the Country model."""

    queryset = models.Coutry.objects.all()
    serializer_class = serializers.CountrySerializer


class CityViewSet(viewsets.ModelViewSet):
    """ViewSet for the City model."""

    queryset = models.City.objects.all()
    serializer_class = serializers.CitySerializer

    def get_serializer_class(self) -> ModelSerializer:
        """Return the appropriate serializer class based on the request."""

        if self.action == "list":
            return serializers.CityListSerializer
        
        if self.action == "retrieve":
            return serializers.CityDetailSerializer
        
        return super().get_serializer_class()


class AirportViewSet(viewsets.ModelViewSet):
    """ViewSet for the Airport model."""

    queryset = models.Airport.objects.all()
    serializer_class = serializers.AirportSerializer


    def get_serializer_class(self) -> ModelSerializer:
        """Return the appropriate serializer class based on the request."""

        if self.action == "list":
            return serializers.AirportListSerializer
        
        if self.action == "retrieve":
            return serializers.AirportDetailSerializer
        
        return super().get_serializer_class()


class RouteViewSet(viewsets.ModelViewSet):
    """ViewSet for the Route model."""

    queryset = models.Route.objects.all()
    serializer_class = serializers.RouteSerializer


    def get_serializer_class(self) -> ModelSerializer:
        """Return the appropriate serializer class based on the request."""

        if self.action == "list":
            return serializers.RouteListSerializer
        
        if self.action == "retrieve":
            return serializers.RouteDetailSerializer
        
        return super().get_serializer_class()


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for the AirplaneType model."""

    queryset = models.AirplaneType.objects.all()
    serializer_class = serializers.AirplaneTypeSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    """ViewSet for the Airplane model."""

    queryset = models.Airplane.objects.all()
    serializer_class = serializers.AirplaneSerializer

    def get_serializer_class(self) -> ModelSerializer:
        """Return the appropriate serializer class based on the request."""

        if self.action == "list":
            return serializers.AirplaneListSerializer
        
        if self.action == "retrieve":
            return serializers.AirplaneDetailSerializer
        
        if self.action == "upload_image":
            return serializers.AirplaneImageSerializer
        
        return super().get_serializer_class()


class FlightViewSet(viewsets.ModelViewSet):
    """ViewSet for the Flight model."""

    queryset = models.Flight.objects.all()
    serializer_class = serializers.FlightSerializer

    def get_serializer_class(self) -> ModelSerializer:
        """Return the appropriate serializer class based on the request."""

        if self.action == "list":
            return serializers.FlightListSerializer
        
        if self.action == "retrieve":
            return serializers.FlightDetailSerializer
        
        return super().get_serializer_class()


class PositionViewSet(viewsets.ModelViewSet):
    """ViewSet for the Position model."""

    queryset = models.Position.objects.all()
    serializer_class = serializers.PositionSerializer


class CrewViewSet(viewsets.ModelViewSet):
    """ViewSet for the Crew model."""

    queryset = models.Crew.objects.all()
    serializer_class = serializers.CrewSerializer

    def get_serializer_class(self) -> ModelSerializer:
        """Return the appropriate serializer class based on the request."""

        if self.action == "list":
            return serializers.CrewListSerializer
        
        if self.action == "retrieve":
            return serializers.CrewDetailSerializer
        
        if self.action == "upload_image":
            return serializers.CrewImageSerializer
        
        return super().get_serializer_class()


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for the Order model."""

    queryset = models.Order.objects.all()
    serializer_class = serializers.OrderSerializer


class TicketViewSet(viewsets.ModelViewSet):
    """ViewSet for the Token model."""

    queryset = models.Ticket.objects.all()
    serializer_class = serializers.TicketSerializer

    def get_serializer_class(self) -> ModelSerializer:
        """Return the appropriate serializer class based on the request."""

        if self.action == "list":
            return serializers.TicketListSerializer
        if self.action == "retrieve":
            return serializers.TicketDetailSerializer

        return super().get_serializer_class()
