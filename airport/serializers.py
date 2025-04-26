from rest_framework import serializers
import airport.models as models


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Coutry
        fields = ("id", "name")


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.City
        fields = ("id", "name", "country")


class CityListSerializer(CitySerializer):
    country = serializers.CharField(source="country.name", read_only=True)


class CityDetailSerializer(CitySerializer):
    country = CountrySerializer()


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Airport
        fields = ("code", "name", "closest_big_city")


class AirportListSerializer(AirportSerializer):
    closest_big_city = serializers.CharField(source="closest_big_city.name", read_only=True)


class AirportDetailSerializer(AirportSerializer):
    closest_big_city = CitySerializer()


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Route
        fields = ("id", "sourse", "destination", "distance")


class RouteListSerializer(RouteSerializer):
    sourse = serializers.CharField(source="sourse.detail_name", read_only=True)
    destination = serializers.CharField(source="destination.detail_name", read_only=True)


class RouteDetailSerializer(serializers.ModelSerializer):
    sourse = AirportListSerializer()
    destination = AirportListSerializer()

    class Meta:
        model = models.Route
        fields = ("id", "sourse", "destination", "distance")


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AirplaneType
        fields = ("id", "name")


class AirplaneSerializer(serializers.ModelSerializer):
    airplane_type = AirplaneTypeSerializer()

    class Meta:
        model = models.Airplane
        fields = ("id", "name", "airplane_type", "image")


class FlightSerializer(serializers.ModelSerializer):
    airplane = AirplaneSerializer()
    route = RouteSerializer()

    class Meta:
        model = models.Flight
        fields = ("id", "airplane", "route", "departure_time", "arrival_time")


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Position
        fields = ("id", "name")


class CrewSerializer(serializers.ModelSerializer):
    position = PositionSerializer()

    class Meta:
        model = models.Crew
        fields = ("id", "first_name", "last_name", "position", "photo")


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Order
        fields = ("id", "created_at", "user")


class TicketSerializer(serializers.ModelSerializer):
    flight = FlightSerializer()
    order = OrderSerializer()

    class Meta:
        model = models.Ticket
        fields = ("id", "flight", "order", "seat", "row")
