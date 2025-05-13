from django.contrib import admin

import airport.models as models
from django.contrib.auth.models import Group

admin.site.register(models.Country)
admin.site.register(models.City)
admin.site.register(models.Airport)
admin.site.register(models.Route)
admin.site.register(models.AirplaneType)
admin.site.register(models.Airplane)
admin.site.register(models.Flight)
admin.site.register(models.Order)
admin.site.register(models.Ticket)
admin.site.register(models.Position)
admin.site.register(models.Crew)
admin.site.unregister(Group)
