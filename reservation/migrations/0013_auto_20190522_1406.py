# Generated by Django 2.2.1 on 2019-05-22 12:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservation', '0012_auto_20190522_1405'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='chargingreservation',
            index=models.Index(fields=['start_time'], name='reservation_start_t_0128c3_idx'),
        ),
        migrations.AddIndex(
            model_name='chargingreservation',
            index=models.Index(fields=['end_time'], name='reservation_end_tim_f12d76_idx'),
        ),
    ]
