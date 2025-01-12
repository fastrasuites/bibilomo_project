# Generated by Django 5.1.4 on 2024-12-24 00:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flights', '0004_alter_flightpackage_placeholder_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingapplication',
            name='is_hidden',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='contactmessage',
            name='is_hidden',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='flightpackage',
            name='is_hidden',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='bookingapplication',
            name='package',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='flights.flightpackage'),
        ),
    ]
