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

    class Meta:
        model = models.City
        fields = ("id", "name", "country")


class CityDetailSerializer(CitySerializer):
    country = CountrySerializer()

    class Meta:
        model = models.City
        fields = ("id", "name", "country")
        read_only_fields = ("id",)


class AirportSerializer(serializers.ModelSerializer):
    closest_big_city = CitySerializer()

    class Meta:
        model = models.Airport
        fields = ("code", "name", "closest_big_city")
        read_only_fields = ("code",)


class RouteSerializer(serializers.ModelSerializer):
    sourse = AirportSerializer()
    destination = AirportSerializer()

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
