import django_filters

import datetime
from datetime import timedelta

from rest_framework import viewsets, filters
from rest_framework.response import Response


from .models import Weather
from .serializer import WeatherSerializer

from django.db.models import Count


class WeatherViewSet(viewsets.ViewSet):

    def list(self, request):
        try:
            from_date = request.GET['from_date']
            to_date = request.GET['to_date']
            period = request.GET['period']
            target = request.GET['target']

            if (from_date < '2018-11-04' or from_date > '2020-11-04'):
                return Response({'result' : 'error'})

            if (to_date < '2018-11-04' or to_date > '2020-11-04'):
                return Response({'result' : 'error'})

            if (from_date > to_date):
                return Response({'result' : 'error'})

            if (period not in ['monthly', 'weekly', 'daily']):
                return Response({'result' : 'error'})

            if (target not in ['precipitation', 'daylight']):
                return Response({'result' : 'error'})
            
            if (period == 'daily'):
                queryset = Weather.objects.raw(
                    'select id, avg(' + target + ') as avg from app_weather where date <= "' + to_date + '" and date >= "' + from_date + '"'
                )

                return Response(
                    {
                        'from': from_date,
                        'to': to_date,
                        'period': period,
                        'target': target,
                        'value' : {
                            'avarage': round(queryset[0].avg, 2), 
                        }
                    }
                )
            elif (period == 'weekly'):
                queryset = Weather.objects.raw(
                    'select id, avg(' + target + ') as avg, strftime("%Y-%W", date) as week from app_weather where date <= "' + to_date + '" and date >= "' + from_date + '" group by week'
                )

                response = []

                for index, item in enumerate(queryset):
                    
                    if item.week[5:] == '00':
                        continue

                    if index == 0:
                        to_dt = (datetime.datetime.strptime(item.week + '-1', "%Y-%W-%w") + timedelta(days=6)).strftime("%Y-%m-%d")
                        response.append(
                            {
                                'from': from_date,
                                'to': to_dt,
                                'period': period,
                                'target': target,
                                'value' : {
                                    'avarage': round(item.avg, 2), 
                                }
                            }
                        )
                    elif index == len(queryset) - 1:
                        from_dt = (datetime.datetime.strptime(item.week + '-1', "%Y-%W-%w")).strftime("%Y-%m-%d")
                        response.append(
                            {
                                'from': from_dt,
                                'to': to_date,
                                'period': period,
                                'target': target,
                                'value' : {
                                    'avarage': round(item.avg, 2), 
                                }
                            }
                        )
                    else:
                        from_dt = (datetime.datetime.strptime(item.week + '-1', "%Y-%W-%w")).strftime("%Y-%m-%d")
                        to_dt = (datetime.datetime.strptime(item.week + '-1', "%Y-%W-%w") + timedelta(days=6)).strftime("%Y-%m-%d")
                        response.append(
                            {
                                'from': from_dt,
                                'to': to_dt,
                                'period': period,
                                'target': target,
                                'value' : {
                                    'avarage': round(item.avg, 2), 
                                }
                            }
                        )
                return Response(response)
            elif (period == 'monthly'):
                queryset = Weather.objects.raw(
                    'select id, avg(' + target + ') as avg, strftime("%Y-%m", date) as month from app_weather where date <= "' + to_date + '" and date >= "' + from_date + '" group by month'
                )

                response = []

                for item in queryset:
                    response.append(
                        {
                            'month': item.month,
                            'period': period,
                            'target': target,
                            'value' : {
                                'avarage': round(item.avg, 2), 
                            }
                        }
                    )

                return Response(response)
            else:
                pass
        except:
            return Response({'result' : 'error'})
