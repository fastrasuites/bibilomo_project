from django.db import models


class FlightPackage(models.Model):
    name = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    origin = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    airline = models.CharField(max_length=255)
    departure_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name