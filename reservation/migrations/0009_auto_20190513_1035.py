# Generated by Django 2.2.1 on 2019-05-13 08:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reservation', '0008_car_charging_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reservation',
            name='is_charging_reservation',
        ),
        migrations.AlterField(
            model_name='car',
            name='charging_time',
            field=models.PositiveIntegerField(verbose_name='Charging time (in hours)'),
        ),
        migrations.CreateModel(
            name='ChargingReservation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('car', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reservation.Car')),
            ],
        ),
    ]
