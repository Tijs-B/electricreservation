import datetime

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Button
from django import forms
from django.contrib import messages
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
        self.request = kwargs.pop('request')

        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _('Create')))

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

        # Check if we could create a new charging reservation
        if self.car.get_distance_left(start_time) < self.cleaned_data['distance']:
            charging_slot = self.car.find_charging_slot(start_time)
            if charging_slot is not None:
                charging_reservation = ChargingReservation(car=self.car,
                                                           start_time=charging_slot,
                                                           end_time=charging_slot + datetime.timedelta(
                                                               hours=self.car.charging_time))
                charging_reservation.save()
                messages.info(
                    self.request,
                    _("We automatically added a charging reservation at %(charging_time)s.")
                    % {'charging_time': charging_slot.strftime('%d %b %Y %H:%M:%S')}
                )


class ReservationDetailForm(forms.ModelForm):
    class Meta:
        fields = ('description', 'distance', 'location', 'start_time', 'end_time', 'priority')
        model = Reservation

    def __init__(self, *args, **kwargs):
        self.car = kwargs.pop('car')
        self.owner = kwargs.pop('owner')
        self.id = kwargs.pop('id')
        self.request = kwargs.pop('request')

        super(ReservationDetailForm, self).__init__(*args, **kwargs)

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
        if not self.car.time_slot_free(start_time, end_time, exclude_reservation_id=self.id):
            raise ValidationError(_("Reservation overlaps with another reservation"))

        # Check if we could create a new charging reservation
        if self.car.get_distance_left(start_time, exclude_reservation_id=self.id) < self.cleaned_data['distance']:
            charging_slot = self.car.find_charging_slot(start_time, exclude_reservation_id=self.id)
            if charging_slot is not None:
                charging_reservation = ChargingReservation(car=self.car,
                                                           start_time=charging_slot,
                                                           end_time=charging_slot + datetime.timedelta(
                                                               hours=self.car.charging_time))
                charging_reservation.save()
                messages.info(
                    self.request,
                    _("We automatically added a charging reservation at %(charging_time)s.")
                    % {'charging_time': charging_slot.strftime('%d %b %Y %H:%M:%S')}
                )


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
            raise ValidationError(_("The car should charge for at least %(charging_time)s hours") %
                                  {'charging_time': self.car.charging_time})


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
            raise ValidationError(_("The car should charge for at least %(charging_time)s hours") %
                                  {'charging_time': self.car.charging_time})


class UserConfigForm(forms.Form):
    email = forms.EmailField(label=_("Email address"), required=False)
    phone_number = forms.CharField(label=_("Phone number"), max_length=12, required=False)

    calendar_color = forms.CharField(label=_("Calendar color"), max_length=7)

    def __init__(self, *args, **kwargs):
        super(UserConfigForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _('Update')))
