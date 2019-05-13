from django.contrib import admin
from reservation.models import Car, Reservation, Profile, ChargingReservation

admin.site.register(Car)
admin.site.register(Reservation)
admin.site.register(ChargingReservation)
admin.site.register(Profile)
