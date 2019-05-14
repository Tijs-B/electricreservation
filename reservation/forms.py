from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Button
from django import forms
from django.contrib.auth.models import User

from reservation.models import Car, Reservation, ChargingReservation


class ReservationDetailForm(forms.ModelForm):

    class Meta:
        fields = ('description', 'distance', 'location', 'start_time', 'end_time', 'should_be_charged_fully', 'priority')
        model = Reservation

    def __init__(self, *args, **kwargs):
        super(ReservationDetailForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Update'))
        self.helper.add_input(Button('delete', 'Delete', onclick="deleteReservation()",
                                     css_class='btn-danger'))


class ReservationAddForm(forms.ModelForm):

    class Meta:
        fields = ('description', 'distance', 'location', 'start_time', 'end_time', 'should_be_charged_fully', 'priority')
        model = Reservation

    def __init__(self, *args, **kwargs):
        super(ReservationAddForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Create'))


class ChargingReservationAddForm(forms.ModelForm):

    class Meta:
        fields = ('start_time', 'end_time')
        model = ChargingReservation

    def __init__(self, *args, **kwargs):
        super(ChargingReservationAddForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Create'))
