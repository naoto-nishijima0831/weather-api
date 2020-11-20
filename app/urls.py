from rest_framework import routers
from django.urls import path

from . import views
from .views import WeatherViewSet



router = routers.DefaultRouter()
router.register('summary', WeatherViewSet, basename='summary')

urlpatterns = [
    path('login/', views.login, name='login'),
]