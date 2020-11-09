from rest_framework import routers
from .views import WeatherViewSet


router = routers.DefaultRouter()
router.register('summary', WeatherViewSet, basename='summary')
