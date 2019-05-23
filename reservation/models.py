import base64
import datetime
import json

import dateutil
import requests
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import ExpressionWrapper, F, DurationField, Sum, Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _
from encrypted_model_fields.fields import EncryptedCharField


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    calendar_color = models.CharField(_("Calendar color"), max_length=7, default='#0275d8')

    phone_regex = RegexValidator(regex=r'^\+\d{11}$',
                                 message=_("Phone number must be entered in the format: '+32496123456'"))
    phone_number = models.CharField(_("Phone number"), validators=[phone_regex], max_length=12, blank=True)

    def __str__(self):
        return f"Profile for {self.user}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Car(models.Model):
    name = models.CharField(_("Name"), max_length=200)

    summer_driving_range = models.PositiveIntegerField(_("Summer driving range"))
    winter_driving_range = models.PositiveIntegerField(_("Winter driving range"))

    charging_time = models.PositiveIntegerField(_("Charging time"))

    users = models.ManyToManyField(User)

    def __str__(self):
        return self.name

    def time_slot_free(self, start_time, end_time, exclude_reservation_id=None, exclude_charging_reservation_id=None):
        reservation_queryset = self.reservation_set
        if exclude_reservation_id is not None:
            reservation_queryset = reservation_queryset.exclude(pk=exclude_reservation_id)

        overlaps_reservation = reservation_queryset \
            .filter(Q(start_time__lt=end_time) & Q(end_time__gt=start_time)) \
            .exists()
        if overlaps_reservation:
            return False

        charging_reservation_queryset = self.chargingreservation_set
        if exclude_charging_reservation_id is not None:
            charging_reservation_queryset = charging_reservation_queryset.exclude(pk=exclude_charging_reservation_id)

        overlaps_charging_reservation = charging_reservation_queryset \
            .filter(Q(start_time__lt=end_time) & Q(end_time__gt=start_time)) \
            .exists()
        if overlaps_charging_reservation:
            return False

        return True

    def get_driving_range(self, time):
        if 4 <= time.month <= 9:
            return self.summer_driving_range
        else:
            return self.winter_driving_range

    def get_last_charging_time_before(self, time):
        last_charging_reservation = self.chargingreservation_set \
            .annotate(diff=ExpressionWrapper(F('end_time') - F('start_time'), output_field=DurationField())) \
            .filter(diff__gte=datetime.timedelta(hours=self.charging_time)) \
            .filter(end_time__lte=time) \
            .order_by('-end_time') \
            .first()
        if last_charging_reservation is None:
            last_charging_time = dateutil.parser.parse("1970-01-01T00:00+00:00")
        else:
            last_charging_time = last_charging_reservation.end_time
        return last_charging_time

    def get_next_charging_time_after(self, time):
        last_charging_reservation = self.chargingreservation_set \
            .annotate(diff=ExpressionWrapper(F('end_time') - F('start_time'), output_field=DurationField())) \
            .filter(diff__gte=datetime.timedelta(hours=self.charging_time)) \
            .filter(start_time__gte=time) \
            .order_by('start_time') \
            .first()
        if last_charging_reservation is None:
            last_charging_time = dateutil.parser.parse("2100-01-01T00:00+00:00")
        else:
            last_charging_time = last_charging_reservation.end_time
        return last_charging_time

    def get_distance_left(self, time, exclude_reservation_id=None):
        last_charging_time = self.get_last_charging_time_before(time)
        queryset = self.reservation_set
        if exclude_reservation_id is not None:
            queryset = queryset.exclude(pk=exclude_reservation_id)
        distance_driven = queryset \
            .filter(start_time__gte=last_charging_time, end_time__lte=time) \
            .aggregate(Sum('distance'))['distance__sum']

        if not distance_driven:
            distance_driven = 0

        return self.get_driving_range(time) - distance_driven

    def find_charging_slot(self, time, exclude_reservation_id=None):
        if self.get_distance_left(time) == self.get_driving_range(time):
            return None

        last_charging_time = self.get_last_charging_time_before(time)
        min_search_time = time - datetime.timedelta(days=3)  # search max 3 days in the past

        # Round time down to half hour and subtract another half hour for spacing
        dt_start_of_hour = time.replace(minute=0, second=0, microsecond=0)
        dt_half_hour = time.replace(minute=30, second=0, microsecond=0)
        if time >= dt_half_hour:
            current_end_time = dt_half_hour
        else:
            current_end_time = dt_start_of_hour

        current_start_time = current_end_time - datetime.timedelta(hours=self.charging_time)
        while current_start_time > last_charging_time and current_start_time > min_search_time:
            if self.time_slot_free(current_start_time, current_end_time, exclude_reservation_id=exclude_reservation_id):
                return current_start_time - datetime.timedelta(minutes=30)
            current_start_time = current_start_time - datetime.timedelta(minutes=30)
            current_end_time = current_end_time - datetime.timedelta(minutes=30)
        return None


# noinspection PyArgumentList
class RenaultServicesLink(models.Model):
    car = models.OneToOneField(Car, blank=True, null=True, on_delete=models.CASCADE)

    username = EncryptedCharField(max_length=100)
    password = EncryptedCharField(max_length=100)

    token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    user_id = models.TextField(blank=True)
    vin = models.CharField(max_length=17)

    last_update = models.DateTimeField(blank=True, null=True)
    UPDATE_INTERVAL = datetime.timedelta(minutes=15)

    charging = models.BooleanField(blank=True, null=True)
    charge_level = models.IntegerField(blank=True, null=True)
    remaining_range = models.FloatField(blank=True, null=True)
    last_battery_status_update = models.DateTimeField(blank=True, null=True)
    charging_point = models.TextField(blank=True)
    remaining_time = models.FloatField(blank=True, null=True)

    def token_expired(self):
        if len(self.token) == 0:
            return True
        payload = self.token.split('.')[1]
        payload = base64.b64decode(payload + '=' * (-len(payload) % 4))
        payload = json.loads(payload)
        exp = datetime.datetime.fromtimestamp(payload['exp'])
        if datetime.datetime.now() > exp:
            return True
        else:
            return False

    def __initialize_tokens(self):
        r = requests.post(
            'https://www.services.renault-ze.com/api/user/login',
            json={"username": self.username, "password": self.password}
        )
        if r.status_code != 200:
            raise ConnectionError("Could not login")
        result = r.json()
        self.token = result['token']
        self.xsrf_token = result['xsrfToken']
        self.user_id = result['user']['id']
        self.vin = result['user']['vehicle_details']['VIN']
        self.save()

    def __refresh_token(self):
        if self.token_expired():
            r = requests.post(
                'https://www.services.renault-ze.com/api/user/token/refresh',
                headers={'Authorization': 'Bearer ' + self.token,
                         'X-XSRF-Token': self.xsrf_token},
                json={'token': self.token}
            )
            if r.status_code != 200:
                raise ConnectionError("Could not refresh token")
            result = r.json()
            self.token = result['token']
            self.save()

    def __update_battery_data(self):
        r = requests.get(
            'https://www.services.renault-ze.com/api/vehicle/' + self.vin + '/battery',
            headers={'Authorization': 'Bearer ' + self.token}
        )
        if r.status_code != 200:
            raise ConnectionError('Could not update battery data')
        result = r.json()
        self.last_update = datetime.datetime.now()
        self.charging = result['charging']
        self.plugged = result['plugged']
        self.charge_level = result['charge_level']
        self.remaining_range = result['remaining_range']
        self.last_battery_status_update = datetime.datetime.fromtimestamp(result['last_update'])

        if result['plugged']:
            self.charging_point = result['charging_point']
        else:
            self.charging_point = ''

        if result['charging']:
            self.remaining_time = result['remaining_time']
        else:
            self.charging = ''

        self.save()

    def update_battery_data(self):
        if self.last_update is None:
            self.__initialize_tokens()
        if self.token_expired():
            self.__refresh_token()
        if self.last_update is None or self.last_update < datetime.datetime.now() - self.UPDATE_INTERVAL:
            self.__update_battery_data()


class Reservation(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    description = models.CharField(_("Description"), max_length=200, default='', blank=True)

    distance = models.PositiveIntegerField(_("Distance"))
    location = models.CharField(_("Location"), max_length=100)

    start_time = models.DateTimeField(_("Start time"))
    end_time = models.DateTimeField(_("End time"))

    should_be_charged_fully = models.BooleanField(_("Should be charged fully"), default=False)

    PRIORITY_LOW = 'L'
    PRIORITY_MEDIUM = 'M'
    PRIORITY_HIGH = 'H'
    PRIORITY_CHOICES = (
        (PRIORITY_LOW, _('Low')),
        (PRIORITY_MEDIUM, _('Medium')),
        (PRIORITY_HIGH, _('High'))
    )
    priority = models.CharField(_("Priority"), choices=PRIORITY_CHOICES, max_length=1, default=PRIORITY_LOW, blank=True)

    def __str__(self):
        return f"Reservation {self.start_time.strftime('%Y-%m-%d %H:%M')}" \
            f"-{self.end_time.strftime('%H:%M')}" \
            f" for {self.car} by {self.owner}"

    class Meta:
        indexes = [
            models.Index(fields=['start_time']),
            models.Index(fields=['end_time']),
        ]


class ChargingReservation(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    start_time = models.DateTimeField(_("Start time"))
    end_time = models.DateTimeField(_("End time"))

    def __str__(self):
        return f"Charging reservation {self.start_time.strftime('%Y-%m-%d %H:%M')}" \
            f"-{self.end_time.strftime('%H:%M')} for {self.car}"

    class Meta:
        indexes = [
            models.Index(fields=['start_time']),
            models.Index(fields=['end_time']),
        ]
