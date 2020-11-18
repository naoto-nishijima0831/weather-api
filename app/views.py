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

    def list(self, request):
        try:
            from_date = datetime.date(int(request.GET['from_date'][0:4]), int(request.GET['from_date'][5:7]), int(request.GET['from_date'][8:10]))

            to_date = datetime.date(int(request.GET['to_date'][0:4]), int(request.GET['to_date'][5:7]), int(request.GET['to_date'][8:10]))

            period, target, area = request.GET['period'], request.GET['target'], request.GET['area']

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

            if (area not in ['Yokohama', 'Tokyo']):
                return Response({
                    'error' : {
                        'message' : '指定エリアが不正です。'
                    }
                })
            
            if (period == 'daily'):
                response = []
                dateFormat = '%Y-%m-%d'
                queryset = Weather.objects.extra(select={'date':'strftime("' + dateFormat + '", date)'}, where=['area="' + area + '"and date>="' + str(from_date) + '" and date<="' + str(to_date) +'"']).values('date').annotate(avg=Avg(target), min=Min(target), max=Max(target))
                for index, item in enumerate(queryset):
                    serializer = ResponseSerializer(
                        data={
                            'from_date': item['date'], 
                            'to_date': item['date'], 
                            'period': period,
                            'target': target,
                            'area': area,
                            'value': {
                                'average': 'No data' if item['avg'] is None else round(item['avg'], 2), 
                                'min': 'No data' if item['min'] is None else round(item['min'], 2),
                                'max': 'No data' if item['max'] is None else round(item['max'], 2),
                            }
                        }
                    )
                    response.append(serializer.initial_data)
                return Response(response)
            elif (period == 'weekly'):
                response = []
                dateFormat = '%Y-%W'
                queryset = Weather.objects.extra(select={'date':'strftime("' + dateFormat + '", date)'}, where=['area="' + area + '"and date>="' + str(from_date) + '" and date<="' + str(to_date) +'"']).values('date').annotate(avg=Avg(target), min=Min(target), max=Max(target))
                for index, item in enumerate(queryset):
                    if item['date'][5:] == '00':
                        continue

                    if index == 0:
                        from_dt = from_date
                        to_dt = (datetime.datetime.strptime(item['date'] + '-1', "%Y-%W-%w") + timedelta(days=6)).strftime("%Y-%m-%d")
                    elif index == len(queryset) - 1:
                        from_dt = datetime.datetime.strptime(item['date'] + '-1', "%Y-%W-%w").strftime("%Y-%m-%d")
                        to_dt = to_date
                    else:
                        from_dt = datetime.datetime.strptime(item['date'] + '-1', "%Y-%W-%w").strftime("%Y-%m-%d")
                        to_dt = (datetime.datetime.strptime(item['date'] + '-1', "%Y-%W-%w") + timedelta(days=6)).strftime("%Y-%m-%d")

                    serializer = ResponseSerializer(
                        data={
                            'from': from_dt,
                            'to': to_dt,
                            'period': period,
                            'target': target,
                            'area': area,
                            'value': {
                                'average': round(item['avg'], 2), 
                                'min': item['min'],
                                'max': item['max'],
                            } 
                        }
                    )

                    response.append(serializer.initial_data)

                return Response(response)
            elif (period == 'monthly'):
                response = []
                dateFormat = '%Y-%m'
                queryset = Weather.objects.extra(select={'date':'strftime("' + dateFormat + '", date)'}, where=['area="' + area + '"and date>="' + str(from_date) + '" and date<="' + str(to_date) +'"']).values('date').annotate(avg=Avg(target), min=Min(target), max=Max(target))
                for index, item in enumerate(queryset):
                    print(item)
                    dt = item['date'] + '-01'

                    if index == 0:
                        from_dt = from_date
                        to_dt = self.get_last_date(from_dt)
                    elif index == len(queryset) - 1:
                        from_dt = datetime.date(int(dt[0:4]), int(dt[5:7]), int(dt[8:10])).replace(day=1)
                        to_dt = to_date
                    else:
                        from_dt = datetime.date(int(dt[0:4]), int(dt[5:7]), int(dt[8:10])).replace(day=1)
                        to_dt = self.get_last_date(from_dt)

                    serializer = ResponseSerializer(
                        data={
                            'from': from_dt,
                            'to': to_dt,
                            'period': period,
                            'target': target,
                            'area': area,
                            'value': {
                                'average': round(item['avg'], 2), 
                                'min': item['min'],
                                'max': item['max'],
                            } 
                        }
                    )
                    response.append(serializer.initial_data)

                return Response(response)
            else:
                pass
        except:
            return Response({
                'error' : {
                    'message' : 'エラーが発生しました。'
                }
            })

    def get_last_date(self, dt):
        return dt.replace(day=calendar.monthrange(dt.year, dt.month)[1])