import django_filters

import datetime
import calendar

from datetime import timedelta

from rest_framework import viewsets, filters
from rest_framework.response import Response


from .models import Weather
from .serializer import ResponseSerializer

from django.db.models import Count, Avg, Max, Min


class WeatherViewSet(viewsets.ViewSet):

    def get_last_date(self, dt):
        return dt.replace(day=calendar.monthrange(dt.year, dt.month)[1])

    def list(self, request):
        try:
            from_date = request.GET['from_date']
            to_date = request.GET['to_date']
            period = request.GET['period']
            target = request.GET['target']

            if (from_date < '2018-11-04' or from_date > '2020-11-04'):
                return Response({
                    'error' : {
                        'message' : '指定可能な日付は、2018年11月4日から2020年11月4日までです。'
                    }
                })

            if (to_date < '2018-11-04' or to_date > '2020-11-04'):
                return Response({
                    'error' : {
                        'message' : '指定可能な日付は、2018年11月4日から2020年11月4日までです。'
                    }
                })

            if (from_date > to_date):
                return Response({
                    'error' : {
                        'message' : '指定日付が不正です。'
                    }
                })

            if (period not in ['monthly', 'weekly', 'daily']):
                return Response({
                    'error' : {
                        'message' : '期間種別が不正です。'
                    }
                })

            if (target not in ['precipitation', 'daylight', 'windspeed']):
                return Response({
                    'error' : {
                        'message' : '集計対象が不正です。'
                    }
                })
            
            if (period == 'daily'):
                queryset = Weather.objects.filter(date__gte=from_date, date__lte=to_date).aggregate(Avg(target), Min(target), Max(target))
                serializer = ResponseSerializer(
                    data={
                        'from_date': from_date, 
                        'to_date': to_date, 
                        'period': period,
                        'target': target,
                        # 'value': {
                            'average': round(queryset[target + '__avg'], 2), 
                            'min': queryset[target + '__min'],
                            'max': queryset[target + '__max'],
                        # }
                    }
                )
                return Response(serializer.initial_data)
            elif (period == 'weekly'):
                queryset = Weather.objects.raw(
                    'select id, avg(' + target + ') as avg, min(' + target + ') as min, max(' + target + ') as max, strftime("%Y-%W", date) as week from app_weather where date <= "' + to_date + '" and date >= "' + from_date + '" group by week'
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
                                # 'value' : {
                                    'average': round(item.avg, 2),
                                    'min': item.min,
                                    'max': item.max, 
                                # }
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
                                # 'value' : {
                                    'average': round(item.avg, 2), 
                                    'min': item.min,
                                    'max': item.max, 
                                # }
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
                                # 'value' : {
                                    'average': round(item.avg, 2), 
                                    'min': item.min,
                                    'max': item.max, 
                                # }
                            }
                        )
                return Response(response)
            elif (period == 'monthly'):
                queryset = Weather.objects.raw(
                    'select id, avg(' + target + ') as avg, min(' + target + ') as min, max(' + target + ') as max, strftime("%Y-%m", date) as month from app_weather where date <= "' + to_date + '" and date >= "' + from_date + '" group by month'
                )

                response = []

                for index, item in enumerate(queryset):
                    if index == 0:
                        dt = datetime.date(int(from_date[0:4]), int(from_date[5:7]), int(from_date[8:10]))
                        to_dt = self.get_last_date(dt)
                        response.append(
                            {
                                'from': from_date,
                                'to': to_dt,
                                'period': period,
                                'target': target,
                                # 'value' : {
                                    'average': round(item.avg, 2), 
                                    'min': item.min,
                                    'max': item.max, 
                                # }
                            }
                        )
                    elif index == len(queryset) - 1:
                        dt = item.month + '-01'
                        from_dt = datetime.date(int(dt[0:4]), int(dt[5:7]), int(dt[8:10])).replace(day=1)
                        response.append(
                            {
                                'from': from_dt,
                                'to': to_date,
                                'period': period,
                                'target': target,
                                # 'value' : {
                                    'average': round(item.avg, 2), 
                                    'min': item.min,
                                    'max': item.max, 
                                # }
                            }
                        )
                    else:
                        from_dt = item.month + '-01'
                        dt = datetime.date(int(from_dt[0:4]), int(from_dt[5:7]), int(from_dt[8:10]))
                        to_dt = self.get_last_date(dt)
                        response.append(
                            {
                                'from': from_dt,
                                'to': to_dt,
                                'period': period,
                                'target': target,
                                # 'value' : {
                                    'average': round(item.avg, 2), 
                                    'min': item.min,
                                    'max': item.max, 
                                # }
                            }
                        )
                return Response(response)
            else:
                pass
        except:
            return Response({
                'error' : {
                    'message' : 'エラーが発生しました。'
                }
            })