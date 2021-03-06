from rest_framework import serializers

from .models import Weather


class WeatherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Weather
        fields = ('date', 'precipitation', 'daylight', 'windspeed', 'area')

class ResponseValueSerializer(serializers.Serializer):
    average = serializers.FloatField()
    min = serializers.FloatField()
    max = serializers.FloatField()

class ResponseSerializer(serializers.Serializer):
    from_date = serializers.DateField()
    to_date = serializers.DateField()
    period = serializers.CharField()
    target = serializers.CharField()
    area = serializers.CharField()
    value = ResponseValueSerializer(required=True)
