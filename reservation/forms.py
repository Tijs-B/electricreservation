from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Button
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Q

from reservation.models import Car, Reservation, ChargingReservation


class ReservationOverlapsMixin:
    def clean(self):
        start_time = self.cleaned_data['start_time']
        end_time = self.cleaned_data['end_time']

        overlaps_reservation = self.car.reservation_set \
            .filter((Q(start_time__lt=start_time) & Q(end_time__gt=start_time))
                    | (Q(start_time__lt=end_time) & Q(end_time__gt=end_time))) \
            .exists()
        if overlaps_reservation:
            raise ValidationError("Reservation overlaps with another reservation")

        overlaps_charging_reservation = self.car.chargingreservation_set \
            .filter((Q(start_time__lt=start_time) & Q(end_time__gt=start_time))
                    | (Q(start_time__lt=end_time) & Q(end_time__gt=end_time))) \
            .exists()
        if overlaps_charging_reservation:
            raise ValidationError("Reservation overlaps with another charging reservation")


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


class ReservationDetailForm(forms.ModelForm):
    class Meta:
        fields = ('description', 'distance', 'location', 'start_time', 'end_time', 'should_be_charged_fully',
                  'priority')
        model = Reservation

    def __init__(self, *args, **kwargs):
        super(ReservationDetailForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Update'))
        self.helper.add_input(Button('delete', 'Delete', onclick="deleteReservation()",
                                     css_class='btn-danger'))


class ChargingReservationAddForm(forms.ModelForm):
    class Meta:
        fields = ('start_time', 'end_time')
        model = ChargingReservation

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


class ChargingReservationDetailForm(forms.ModelForm):
    class Meta:
        fields = ('start_time', 'end_time')
        model = ChargingReservation

    def __init__(self, *args, **kwargs):
        super(ChargingReservationDetailForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Update'))
        self.helper.add_input(Button('delete', 'Delete', onclick="deleteReservation()",
                                     css_class='btn-danger'))
