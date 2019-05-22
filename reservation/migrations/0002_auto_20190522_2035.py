# Generated by Django 2.2.1 on 2019-05-22 18:35

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservation', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='charging_time',
            field=models.PositiveIntegerField(verbose_name='Charging time'),
        ),
        migrations.AlterField(
            model_name='car',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='car',
            name='summer_driving_range',
            field=models.PositiveIntegerField(verbose_name='Summer driving range'),
        ),
        migrations.AlterField(
            model_name='car',
            name='winter_driving_range',
            field=models.PositiveIntegerField(verbose_name='Winter driving range'),
        ),
        migrations.AlterField(
            model_name='chargingreservation',
            name='end_time',
            field=models.DateTimeField(verbose_name='End time'),
        ),
        migrations.AlterField(
            model_name='chargingreservation',
            name='start_time',
            field=models.DateTimeField(verbose_name='Start time'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='calendar_color',
            field=models.CharField(max_length=7, verbose_name='Calendar color'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='phone_number',
            field=models.CharField(blank=True, max_length=12, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+32496123456'", regex='^\\+\\d{11}$')], verbose_name='Phone number'),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='description',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='distance',
            field=models.PositiveIntegerField(verbose_name='Distance'),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='end_time',
            field=models.DateTimeField(verbose_name='End time'),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='location',
            field=models.CharField(max_length=100, verbose_name='Location'),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='priority',
            field=models.CharField(blank=True, choices=[('L', 'Low'), ('M', 'Medium'), ('H', 'High')], default='L', max_length=1, verbose_name='Priority'),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='should_be_charged_fully',
            field=models.BooleanField(default=False, verbose_name='Should be charged fully'),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='start_time',
            field=models.DateTimeField(verbose_name='Start time'),
        ),
    ]
