import datetime

import dateutil
from django.contrib.auth.models import User
from django.db import models
from django.db.models import ExpressionWrapper, F, DurationField, Sum, Q
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    calendar_color = models.CharField(max_length=7)

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
    name = models.CharField(max_length=200)

    summer_driving_range = models.PositiveIntegerField(verbose_name="Summer driving range (km)")
    winter_driving_range = models.PositiveIntegerField(verbose_name="Winter driving range (km)")

    charging_time = models.PositiveIntegerField(verbose_name="Charging time (in hours)")

    users = models.ManyToManyField(User)

    def __str__(self):
        return self.name

    def time_slot_free(self, start_time, end_time, exclude_reservation_id=None, exclude_charging_reservation_id=None):
        reservation_queryset = self.reservation_set
        if exclude_reservation_id is not None:
            reservation_queryset = reservation_queryset.exclude(pk=exclude_reservation_id)

        overlaps_reservation = reservation_queryset.exclude(pk=self.id) \
            .filter((Q(start_time__lte=start_time) & Q(end_time__gt=start_time))
                    | (Q(start_time__lt=end_time) & Q(end_time__gte=end_time))) \
            .exists()
        if overlaps_reservation:
            return False

        charging_reservation_queryset = self.chargingreservation_set
        if exclude_charging_reservation_id is not None:
            charging_reservation_queryset = charging_reservation_queryset.exclude(pk=exclude_charging_reservation_id)

        overlaps_charging_reservation = charging_reservation_queryset \
            .filter((Q(start_time__lt=start_time) & Q(end_time__gt=start_time))
                    | (Q(start_time__lt=end_time) & Q(end_time__gt=end_time))) \
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


class Reservation(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    description = models.CharField(max_length=200, default='', blank=True)

    distance = models.PositiveIntegerField(verbose_name="Distance (km)")
    location = models.CharField(max_length=100)

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    should_be_charged_fully = models.BooleanField(default=False)

    PRIORITY_LOW = 'L'
    PRIORITY_MEDIUM = 'M'
    PRIORITY_HIGH = 'H'
    PRIORITY_CHOICES = (
        (PRIORITY_LOW, 'Low'),
        (PRIORITY_MEDIUM, 'Medium'),
        (PRIORITY_HIGH, 'High')
    )
    priority = models.CharField(choices=PRIORITY_CHOICES, max_length=1, default=PRIORITY_LOW, blank=True)

    def __str__(self):
        return f"Reservation {self.start_time.strftime('%Y-%m-%d %H:%M')}" \
            f"-{self.end_time.strftime('%H:%M')}" \
            f" for {self.car} by {self.owner}"


class ChargingReservation(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"Charging reservation {self.start_time.strftime('%Y-%m-%d %H:%M')}" \
            f"-{self.end_time.strftime('%H:%M')} for {self.car}"
