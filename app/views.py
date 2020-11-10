import django_filters
from rest_framework import viewsets, filters
from rest_framework.response import Response


from .models import Weather
from .serializer import WeatherSerializer

from django.db.models import Count


class WeatherViewSet(viewsets.ViewSet):

    def list(self, request):
        try:
            start = request.GET['start']
            end = request.GET['end']

            period = request.GET['period']

            target = request.GET['target']

            if (period != 'monthly' and period != 'weekly' and period != 'daily'):
                return Response({'result' : 'error'})

            if (target != 'precipitation' and target != 'daylight'):
                return Response({'result' : 'error'})
            
            queryset = Weather.objects.raw(
                'select id, avg(' + target + ') as avg from app_weather where date <= "' + end + '" and date >= "' + start + '"'
            )

            return Response({'result' : round(queryset[0].avg, 2)})
        except:
            return Response({'result' : 'error'})
