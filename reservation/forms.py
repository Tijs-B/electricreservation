from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Button
from django import forms
from django.core.exceptions import ValidationError

from reservation.models import Reservation, ChargingReservation


class ReservationAddForm(forms.ModelForm):
    class Meta:
        fields = ('description', 'distance', 'location', 'start_time', 'end_time', 'should_be_charged_fully',
                  'priority')
        model = Reservation

    def __init__(self, *args, **kwargs):
        self.car = kwargs.pop('car')
        self.owner = kwargs.pop('owner')
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Create'))

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.car = self.car
        instance.owner = self.owner
        if commit:
            instance.save()
        return instance

    def clean(self):
        start_time = self.cleaned_data['start_time']
        end_time = self.cleaned_data['end_time']

        # Check start_time < end_time
        if start_time >= end_time:
            raise ValidationError("End time must come after start time")

        # Check overlap
        if not self.car.time_slot_free(start_time, end_time):
            raise ValidationError("Reservation overlaps with another reservation")

        # Check enough distance left
        distance_left = self.car.get_distance_left(start_time)
        if distance_left < self.cleaned_data['distance']:
            raise ValidationError(f"The car doesn't have enough distance left (need {self.cleaned_data['distance']} "
                                  f"km, {distance_left} km left)")

        # Check no other reservations could get into trouble
        next_charging_time = self.car.get_next_charging_time_after(end_time)
        last_reservation = Reservation.objects \
            .filter(start_time__gte=end_time, end_time__lte=next_charging_time) \
            .order_by('-start_time') \
            .first()

        if last_reservation:
            distance_left_at_last = self.car.get_distance_left(last_reservation.start_time)
            if distance_left_at_last - self.cleaned_data['distance'] < last_reservation.distance:
                raise ValidationError(f"Making this reservation would mean that at least one other reservation would "
                                      f"be cancelled, including a reservation to "
                                      f"{last_reservation.location.capitalize()} made by "
                                      f"{last_reservation.owner.username.capitalize()}")


class ReservationDetailForm(forms.ModelForm):
    class Meta:
        fields = ('description', 'distance', 'location', 'start_time', 'end_time', 'should_be_charged_fully',
                  'priority')
        model = Reservation

    def __init__(self, *args, **kwargs):
        self.car = kwargs.pop('car')
        self.owner = kwargs.pop('owner')
        self.id = kwargs.pop('id')
        super(ReservationDetailForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Update'))
        self.helper.add_input(Button('delete', 'Delete', onclick="deleteReservation()",
                                     css_class='btn-danger'))

    def clean(self):
        start_time = self.cleaned_data['start_time']
        end_time = self.cleaned_data['end_time']

        # Check start_time < end_time
        if start_time >= end_time:
            raise ValidationError("End time must come after start time")

        # Check overlap
        if not self.car.time_slot_free(start_time, end_time, exclude_reservation_id=self.id):
            raise ValidationError("Reservation overlaps with another reservation")

        # Check enough distance left
        distance_left = self.car.get_distance_left(start_time, exclude_reservation_id=self.id)
        if distance_left < self.cleaned_data['distance']:
            raise ValidationError(f"The car doesn't have enough distance left (need {self.cleaned_data['distance']} "
                                  f"km, {distance_left} km left)")

        # Check no other reservations could get into trouble
        next_charging_time = self.car.get_next_charging_time_after(end_time)
        last_reservation = Reservation.objects.exclude(pk=self.id) \
            .filter(start_time__gte=end_time, end_time__lte=next_charging_time) \
            .order_by('-start_time') \
            .first()

        if last_reservation:
            distance_left_at_last = self.car.get_distance_left(last_reservation.start_time,
                                                               exclude_reservation_id=self.id)
            if distance_left_at_last - self.cleaned_data['distance'] < last_reservation.distance:
                raise ValidationError(f"Making this reservation would mean that at least one other reservation would "
                                      f"be cancelled, including a reservation to {last_reservation.location} made by "
                                      f"{last_reservation.owner.username.capitalize()}")


class ChargingReservationAddForm(forms.ModelForm):
    class Meta:
        model = ChargingReservation
        fields = ('start_time', 'end_time')
        widgets = {
            'end_time': forms.TextInput(attrs={'readonly': True})
        }

    def __init__(self, *args, **kwargs):
        self.car = kwargs.pop('car')
        super(ChargingReservationAddForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Create'))

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.car = self.car
        if commit:
            instance.save()
        return instance

    def clean(self):
        start_time = self.cleaned_data['start_time']
        end_time = self.cleaned_data['end_time']

        # Check start_time < end_time
        if start_time >= end_time:
            raise ValidationError("End time must come after start time")

        # Check overlap
        if not self.car.time_slot_free(start_time, end_time):
            raise ValidationError("Reservation overlaps with another reservation")

        # Check charging time
        charging_time = self.cleaned_data['end_time'] - self.cleaned_data['start_time']
        if charging_time.total_seconds() < self.car.charging_time * 60 * 60:
            raise ValidationError(f"The car should charge for at least {self.car.charging_time} hours")


class ChargingReservationDetailForm(forms.ModelForm):
    class Meta:
        model = ChargingReservation
        fields = ('start_time', 'end_time')
        widgets = {
            'end_time': forms.TextInput(attrs={'readonly': True})
        }

    def __init__(self, *args, **kwargs):
        self.car = kwargs.pop('car')
        self.id = kwargs.pop('id')
        super(ChargingReservationDetailForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Update'))
        self.helper.add_input(Button('delete', 'Delete', onclick="deleteReservation()",
                                     css_class='btn-danger'))

    def clean(self):
        start_time = self.cleaned_data['start_time']
        end_time = self.cleaned_data['end_time']

        # Check start_time < end_time
        if start_time >= end_time:
            raise ValidationError("End time must come after start time")

        # Check overlap
        if not self.car.time_slot_free(start_time, end_time, exclude_charging_reservation_id=self.id):
            raise ValidationError("Reservation overlaps with another reservation")

        # Check charging time
        charging_time = self.cleaned_data['end_time'] - self.cleaned_data['start_time']
        if charging_time.total_seconds() < self.car.charging_time * 60 * 60:
            raise ValidationError(f"The car should charge for at least {self.car.charging_time} hours")
