from django.contrib import admin
from .models import Weather

# Register your models here.
@admin.register(Weather)
class Weather(admin.ModelAdmin):
    pass
