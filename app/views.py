import django_filters
from rest_framework import viewsets, filters
from rest_framework.response import Response


from .models import Weather
from .serializer import WeatherSerializer

from django.db.models import Count


class WeatherViewSet(viewsets.ViewSet):

    def list(self, request):
        start = (request.GET['start'])
        end = (request.GET['end'])

        target = (request.GET['target'])

        if (target == 'precipitation' or target == 'daylight'):
            queryset = Weather.objects.raw(
                'select id, avg(' + target + ') as avg from app_weather where date <= "' + end + '" and date >= "' + start + '"'
            )
            serializer = WeatherSerializer(queryset, many=True)
            return Response({'result' : queryset[0].avg})
        else:
            return Response({'result' : 'error'})
