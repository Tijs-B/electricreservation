from django.contrib.auth.models import User
from rest_framework import serializers

from reservation.models import Reservation, Car, Profile, ChargingReservation, RenaultServicesLink


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('calendar_color',)


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'profile')


class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ('id', 'name', 'summer_driving_range', 'winter_driving_range', 'users', 'charging_time')


class RenaultServicesLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = RenaultServicesLink
        fields = ('id', 'last_update', 'charging', 'plugged', 'charge_level', 'remaining_range',
                  'last_battery_status_update', 'charging_point', 'remaining_time')


class ReservationSerializer(serializers.ModelSerializer):
    owner = UserSerializer()
    distance_left = serializers.SerializerMethodField()

    def get_distance_left(self, reservation):
        return reservation.car.get_distance_left(reservation.start_time)

    class Meta:
        model = Reservation
        fields = ('id', 'owner', 'car', 'description', 'distance', 'location', 'start_time', 'end_time',
                  'should_be_charged_fully', 'priority', 'distance_left')


class ChargingReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChargingReservation
        fields = ('id', 'car', 'start_time', 'end_time')
