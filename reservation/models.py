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

    summer_driving_range = models.PositiveIntegerField()
    winter_driving_range = models.PositiveIntegerField()

    users = models.ManyToManyField(User)

    def __str__(self):
        return self.name


class Reservation(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    description = models.CharField(max_length=200, default='', blank=True)

    distance = models.PositiveIntegerField(null=True)
    location = models.CharField(max_length=100, default='', blank=True)

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    should_be_charged_fully = models.BooleanField(blank=True, default=False)

    PRIORITY_LOW = 'L'
    PRIORITY_MEDIUM = 'M'
    PRIORITY_HIGH = 'H'
    PRIORITY_CHOICES = (
        (PRIORITY_LOW, 'Low'),
        (PRIORITY_MEDIUM, 'Medium'),
        (PRIORITY_HIGH, 'High')
    )
    priority = models.CharField(choices=PRIORITY_CHOICES, max_length=1, default=PRIORITY_LOW, blank=True)

    is_charging_reservation = models.BooleanField(default=False)

    def __str__(self):
        if self.is_charging_reservation:
            return f"Charging reservation for {self.car} from {self.start_time} to {self.end_time}"
        else:
            return f"Reservation for {self.car} from {self.start_time} to {self.end_time}"
