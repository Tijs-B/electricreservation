from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Button
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from reservation.models import Reservation, ChargingReservation


class ReservationAddForm(forms.ModelForm):
    class Meta:
        fields = ('description', 'distance', 'location', 'start_time', 'end_time', 'priority')
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
            raise ValidationError(_("End time must come after start time"))

        # Check overlap
        if not self.car.time_slot_free(start_time, end_time):
            raise ValidationError(_("Reservation overlaps with another reservation"))


class ReservationDetailForm(forms.ModelForm):
    class Meta:
        fields = ('description', 'distance', 'location', 'start_time', 'end_time', 'priority')
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
            raise ValidationError(_("End time must come after start time"))

        # Check overlap
        if not self.car.time_slot_free(start_time, end_time, exclude_reservation_id=self.id):
            raise ValidationError(_("Reservation overlaps with another reservation"))


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
        self.helper.add_input(Submit('submit', _('Create')))

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
            raise ValidationError(_("End time must come after start time"))

        # Check overlap
        if not self.car.time_slot_free(start_time, end_time):
            raise ValidationError(_("Reservation overlaps with another reservation"))

        # Check charging time
        charging_time = self.cleaned_data['end_time'] - self.cleaned_data['start_time']
        if charging_time.total_seconds() < self.car.charging_time * 60 * 60:
            raise ValidationError(_("The car should charge for at least %(charging_time)s hours" %
                                    {'charging_time': self.car.charging_time}))


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
        self.helper.add_input(Submit('submit', _('Update')))
        self.helper.add_input(Button('delete', _('Delete'), onclick="deleteReservation()",
                                     css_class='btn-danger'))

    def clean(self):
        start_time = self.cleaned_data['start_time']
        end_time = self.cleaned_data['end_time']

        # Check start_time < end_time
        if start_time >= end_time:
            raise ValidationError(_("End time must come after start time"))

        # Check overlap
        if not self.car.time_slot_free(start_time, end_time, exclude_charging_reservation_id=self.id):
            raise ValidationError(_("Reservation overlaps with another reservation"))

        # Check charging time
        charging_time = self.cleaned_data['end_time'] - self.cleaned_data['start_time']
        if charging_time.total_seconds() < self.car.charging_time * 60 * 60:
            raise ValidationError(_("The car should charge for at least %(charging_time)s hours" %
                                    {'charging_time': self.car.charging_time}))
