from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    calendar_color = models.CharField(max_length=7)

    def __str__(self):
        return str(self.user)


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
        return f"Reservation for {self.car} from {self.start_time} to {self.end_time}"


class ChargingReservation(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"Charging reservation for {self.car} from {self.start_time} to {self.end_time}"
