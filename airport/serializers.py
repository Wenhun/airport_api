from rest_framework import serializers
import airport.models as models


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Country
        fields = ("id", "name")


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.City
        fields = ("id", "name", "country")


class CityListSerializer(CitySerializer):
    country = serializers.CharField(source="country.name", read_only=True)


class CityDetailSerializer(CitySerializer):
    country = CountrySerializer(read_only=True, many=False)


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Airport
        fields = ("code", "name", "closest_big_city")


class AirportListSerializer(AirportSerializer):
    closest_big_city = serializers.CharField(source="closest_big_city.name", read_only=True)


class AirportDetailSerializer(AirportSerializer):
    closest_big_city = CitySerializer(read_only=True, many=False)


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(RouteSerializer):
    sourse = serializers.CharField(source="source.detail_name", read_only=True)
    destination = serializers.CharField(source="destination.detail_name", read_only=True)


class RouteDetailSerializer(serializers.ModelSerializer):
    sourse = AirportListSerializer(read_only=True, many=False)
    destination = AirportListSerializer(read_only=True, many=False)

    class Meta:
        model = models.Route
        fields = ("id", "source", "destination", "distance")


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AirplaneType
        fields = ("id", "name")


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Airplane
        fields = ("id", "name", "airplane_type", "rows", "seats_in_row", "image")


class AirplaneListSerializer(AirplaneSerializer):
    airplane_type = serializers.CharField(source="airplane_type.name", read_only=True)


class AirplaneDetailSerializer(AirplaneSerializer):
    airplane_type = AirplaneTypeSerializer(read_only=True, many=False)


class AirplaneImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Airplane
        fields = ("id", "image")


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Position
        fields = ("id", "name")


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Crew
        fields = ("id", "first_name", "last_name", "position", "photo")


class CrewListSerializer(CrewSerializer):
    position = serializers.CharField(source="position.name", read_only=True)


class CrewDetailSerializer(CrewSerializer):
    position = PositionSerializer(read_only=True, many=False)


class CrewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Crew
        fields = ("id", "photo")


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Flight
        fields = ("id", "airplane", "route", "crew", "departure_time", "arrival_time")


class FlightListSerializer(FlightSerializer):
    airplane = serializers.CharField(source="airplane.name", read_only=True)
    route = serializers.CharField(source="route.__str__", read_only=True)
    departure_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    arrival_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    crew = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="full_name")


class FlightDetailSerializer(FlightSerializer):
    airplane = AirplaneListSerializer(read_only=True, many=False)
    route = RouteListSerializer(read_only=True, many=False)
    crew = CrewDetailSerializer(many=True, read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Order
        fields = ("id", "created_at", "user")


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Ticket
        fields = ("id", "flight", "order", "seat", "row")


class TicketListSerializer(TicketSerializer):
    flight = serializers.CharField(source="flight.__str__")
    order = serializers.CharField(source="order.__str__")


class TicketDetailSerializer(TicketSerializer):
    flight = FlightListSerializer(many=False)
    order = OrderSerializer(many=False)
