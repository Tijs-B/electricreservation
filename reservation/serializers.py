from django.contrib.auth.models import User
from rest_framework import serializers

from reservation.models import Reservation, Car


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ('id', 'name', 'summer_driving_range', 'winter_driving_range', 'users')


class ReservationSerializer(serializers.ModelSerializer):
    owner = UserSerializer()


    class Meta:
        model = Reservation
        fields = ('id', 'owner', 'car', 'description', 'distance', 'location', 'start_time', 'end_time',
                  'should_be_charged_fully', 'priority', 'is_charging_reservation')
