import datetime

from django.db import models
from django.utils import timezone

from django_ckeditor_5.fields import CKEditor5Field


class FlightPackage(models.Model):
    name = models.CharField(max_length=255)
    flight_mode = models.CharField(max_length=255, choices=[
        ('one_way', 'One Way'),
        ('round_trip', 'Round Trip'),
        ('multi_city', 'Multi City')
    ], default='one_way')
    destination = models.CharField(max_length=255)
    placeholder_image = models.ImageField(upload_to='flight_images',
                                          default='https://placehold.co/600x400/000000/FFFFFF.svg')
    flight_class = models.CharField(max_length=255, choices=[
        ('economy', 'Economy'),
        ('economy_plus', 'Economy Plus'),
        ('business', 'Business'),
        ('first_class', 'First Class')], default='economy')
    origin = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    airline = models.CharField(max_length=255)
    departure_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    def __str__(self):
        return self.name

    def count(self):
        return self.objects.all().count()

    def recent_count(self):
        one_week_ago = timezone.now() - datetime.timedelta(days=7)
        return self.objects.filter(date_created__gte=one_week_ago).count()


class BookingApplication(models.Model):
    package = models.ForeignKey(FlightPackage, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    number_of_passengers = models.IntegerField()
    phone_number = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=[('m', 'Male'), ('f', 'Female')])
    nationality = models.CharField(max_length=255)
    date_booked = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    def __str__(self):
        return self.full_name

    def count(self):
        return self.objects.all().count()

    def recent_count(self):
        one_week_ago = timezone.now() - datetime.timedelta(days=7)
        return self.objects.filter(date_booked__gte=one_week_ago).count()


class ContactMessage(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    message = CKEditor5Field()
    date_sent = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    def __str__(self):
        return self.full_name

    def count(self):
        return self.objects.all().count()

    def recent_count(self):
        one_week_ago = timezone.now() - datetime.timedelta(days=7)
        return self.objects.filter(date_sent__gte=one_week_ago).count()
