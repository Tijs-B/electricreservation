from django import forms

from reservation.models import Car, Reservation


class CarConfigForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ('name', 'summer_driving_range', 'winter_driving_range')


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ('description', 'distance', 'location', 'start_time', 'end_time', 'should_be_charged_fully',
                  'priority')
