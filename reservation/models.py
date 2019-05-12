from django.db import models
from django.contrib.auth.models import User


class Car(models.Model):
    name = models.CharField(max_length=200)

    summer_driving_range = models.PositiveIntegerField()
    winter_driving_range = models.PositiveIntegerField()

    users = models.ManyToManyField(User)

    def __str__(self):
        return self.name


class Reservation(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    description = models.CharField(max_length=200, default='')

    distance = models.PositiveIntegerField(blank=True, default=0)
    location = models.CharField(max_length=100, default='')

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
        return f"Reservation for {self.car} from {self.start_time} to {self.end_time}"

