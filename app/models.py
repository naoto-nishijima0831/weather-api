from django.db import models

class Weather(models.Model):
    date = models.DateField(null=True)
    precipitation = models.FloatField(null=True)
    daylight = models.FloatField(null=True)
    windspeed = models.FloatField(null=True)
    area = models.TextField(null=True)