from __future__ import annotations

import os
import uuid
from django.utils.text import slugify
from django.conf import settings

from django.core.exceptions import ValidationError


from django.db import models


class Country(models.Model):
    """Model representing a country."""

    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = "countries"

    def __str__(self) -> str:
        return self.name


class City(models.Model):
    """Model representing a city."""

    name = models.CharField(max_length=255)
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, related_name="cities")
    
    class Meta:
        verbose_name_plural = "cities"

    def __str__(self) -> str:
        return self.name


class Airport(models.Model):
    """Model representing an airport."""

    code = models.CharField(max_length=3, unique=True, primary_key=True)
    name = models.CharField(max_length=255)
    closest_big_city = models.ForeignKey(City, on_delete=models.CASCADE)

    @property
    def detail_name(self) -> str:
        """Return the full name of the airport."""
        return f"{self.code} ({self.closest_big_city.name})"

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"


class Route(models.Model):
    """Model representing a route."""

    source = models.ForeignKey(
        Airport, related_name="source", on_delete=models.CASCADE)
    destination = models.ForeignKey(
        Airport, related_name="destination", on_delete=models.CASCADE
    )
    distance = models.FloatField()

    def __str__(self) -> str:
        return f"{self.source.detail_name} - {self.destination.detail_name}"


class AirplaneType(models.Model):
    """Model representing an airplane type."""

    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name


class Airplane(models.Model):
    """Model representing an airplane."""

    def plane_image_file_path(instance: "Airplane", filename: str) -> str:
        """Generate a file path for the airplane image."""
        _, extension = os.path.splitext(filename)
        filename = f"{slugify(instance.name)}-{uuid.uuid4()}{extension}"
        return os.path.join("uploads", "planes", filename)

    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(AirplaneType, on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to=plane_image_file_path, blank=True, null=True)

    @property
    def capacity(self) -> int:
        """Calculate and return the total seating capacity of the airplane."""
        return self.rows * self.seats_in_row

    def __str__(self) -> str:
        return f"{self.name} Capacity: {self.capacity}"


class Position(models.Model):
    """Model representing a position crew member."""

    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        """Return the string representation of the position."""
        return self.name


class Crew(models.Model):
    """Model representing a crew member."""

    def crew_photo_file_path(instance: "Crew", filename: str) -> str:
        """Generate a file path for the crew member's photo."""
        _, extension = os.path.splitext(filename)
        filename = f"{slugify(instance.full_name)}-{uuid.uuid4()}{extension}"
        return os.path.join("uploads", "crew_photos", filename)

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    photo = models.ImageField(
        upload_to=crew_photo_file_path, blank=True, null=True)

    @property
    def full_name(self) -> str:
        """Return the full name of the crew member."""
        return f"{self.first_name} {self.last_name}"

    def __str__(self) -> str:
        return f"{self.full_name}"


class Flight(models.Model):
    """Model representing a flight."""

    flight_number = models.CharField(max_length=255, unique=True)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    crew = models.ManyToManyField(Crew, related_name="flights", db_index=True)
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    class Meta:
        ordering = ["-departure_time"]

    def __str__(self) -> str:
        """Return the string representation of the flight."""
        return f"{self.flight_number} Departure: {self.departure_time}"


class Order(models.Model):
    """Model representing an order."""

    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"Order {self.id} created: {self.created_at}"

    class Meta:
        ordering = ["-created_at"]


class Ticket(models.Model):
    """Model representing a ticket."""

    class SeatChoices(models.IntegerChoices):
        A = 1, "A"
        B = 2, "B"
        C = 3, "C"
        D = 4, "D"
        E = 5, "E"
        F = 6, "F"
        G = 7, "G"
        H = 8, "H"
        I = 9, "I"
        J = 10, "J"

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    row = models.IntegerField()
    seat = models.IntegerField(choices=SeatChoices.choices)

    def __str__(self) -> str:
        return f"{self.flight} - {self.row}{self.seat}"

    @staticmethod
    def validate_ticket(
        row: int,
        seat: int,
        airplane: Airplane,
        error_to_raise: type[ValidationError]
    ) -> None:
        for ticket_attr_value, ticket_attr_name, airplane_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row"),
        ]:
            count_attrs = getattr(airplane, airplane_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                        f"number must be in available range: "
                        f"(1, {airplane_attr_name}): "
                        f"(1, {count_attrs})"
                    }
                )

    def clean(self) -> None:
        """
        Perform custom validation for the Ticket model.

        Ensures that the ticket's
            row and seat are valid for the associated airplane.
        """
        Ticket.validate_ticket(
            self.row,
            self.seat,
            self.flight.airplane,
            ValidationError,
        )

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: str | None = None,
        update_fields: list[str] | None = None,
    ) -> Ticket:
        """
        Save the Ticket instance after performing validation.

        Args:
            force_insert (bool): Whether to force an SQL INSERT.
            force_update (bool): Whether to force an SQL UPDATE.
            using (str | None): The database alias to use.
            update_fields (list[str] | None): The fields to update.

        Returns:
            Ticket: The saved Ticket instance.
        """
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    class Meta:
        unique_together = ("flight", "row", "seat")
        ordering = ["flight", "row", "seat"]
