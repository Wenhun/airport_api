from django.shortcuts import render

import airport.models as models
import airport.serializers as serializers

from rest_framework import viewsets


class CountryViewSet(viewsets.ModelViewSet):
    """ViewSet for the Country model."""

    queryset = models.Coutry.objects.all()
    serializer_class = serializers.CountrySerializer


class CityViewSet(viewsets.ModelViewSet):
    """ViewSet for the City model."""

    queryset = models.City.objects.all()
    serializer_class = serializers.CitySerializer


class AirportViewSet(viewsets.ModelViewSet):
    """ViewSet for the Airport model."""

    queryset = models.Airport.objects.all()
    serializer_class = serializers.AirportSerializer


class RouteViewSet(viewsets.ModelViewSet):
    """ViewSet for the Route model."""

    queryset = models.Route.objects.all()
    serializer_class = serializers.RouteSerializer


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for the AirplaneType model."""

    queryset = models.AirplaneType.objects.all()
    serializer_class = serializers.AirplaneTypeSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    """ViewSet for the Airplane model."""

    queryset = models.Airplane.objects.all()
    serializer_class = serializers.AirplaneSerializer


class FlightViewSet(viewsets.ModelViewSet):
    """ViewSet for the Flight model."""

    queryset = models.Flight.objects.all()
    serializer_class = serializers.FlightSerializer


class PositionViewSet(viewsets.ModelViewSet):
    """ViewSet for the Position model."""

    queryset = models.Position.objects.all()
    serializer_class = serializers.PositionSerializer


class CrewViewSet(viewsets.ModelViewSet):
    """ViewSet for the Crew model."""

    queryset = models.Crew.objects.all()
    serializer_class = serializers.CrewSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for the Order model."""

    queryset = models.Order.objects.all()
    serializer_class = serializers.OrderSerializer


class TicketViewSet(viewsets.ModelViewSet):
    """ViewSet for the Token model."""

    queryset = models.Ticket.objects.all()
    serializer_class = serializers.TicketSerializer
