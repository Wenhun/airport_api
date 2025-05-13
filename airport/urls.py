from django.urls import path, include
from rest_framework import routers

import airport.views as views

app_name = "airport"

router = routers.DefaultRouter()
router.register(r"country", views.CountryViewSet, basename="country")
router.register(r"city", views.CityViewSet, basename="city")
router.register(r"airport", views.AirportViewSet, basename="airport")
router.register(r"route", views.RouteViewSet, basename="route")
router.register(
    r"airplane-type", views.AirplaneTypeViewSet, basename="airplane-type")
router.register(r"airplane", views.AirplaneViewSet, basename="airplane")
router.register(r"flight", views.FlightViewSet, basename="flight")
router.register(r"position", views.PositionViewSet, basename="position")
router.register(r"crew", views.CrewViewSet, basename="crew")
router.register(r"order", views.OrderViewSet, basename="order")
router.register(r"ticket", views.TicketViewSet, basename="ticket")

urlpatterns = [path("", include(router.urls))]
