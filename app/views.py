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
            from_date, to_date, period, target, area = request.GET['from_date'], request.GET['to_date'], request.GET['period'], request.GET['target'], request.GET['area']

            # if (from_date < '2018-11-04' or from_date > '2020-11-04' or to_date < '2018-11-04' or to_date > '2020-11-04'):
            #     return Response({
            #         'error' : {
            #             'message' : '指定可能な日付は、2018年11月4日から2020年11月4日までです。'
            #         }
            #     })

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

                start = datetime.date(int(from_date[0:4]), int(from_date[5:7]), int(from_date[8:10]))
                end = datetime.date(int(to_date[0:4]), int(to_date[5:7]), int(to_date[8:10]))

                for i in range((end - start).days + 1):
                    date = str(start + timedelta(i))
                    queryset = Weather.objects.filter(date__gte=date, date__lte=date, area=area).aggregate(Avg(target), Min(target), Max(target))
                    serializer = ResponseSerializer(
                        data={
                            'from_date': date, 
                            'to_date': date, 
                            'period': period,
                            'target': target,
                            'area': area,
                            'value': {
                                'average': 'No data' if queryset[target + '__avg'] is None else round(queryset[target + '__avg'], 2), 
                                'min': 'No data' if queryset[target + '__min'] is None else round(queryset[target + '__min'], 2),
                                'max': 'No data' if queryset[target + '__max'] is None else round(queryset[target + '__max'], 2),
                            }
                        }
                    )
                    response.append(serializer.initial_data)
                return Response(response)
            elif (period == 'weekly'):
                queryset = Weather.objects.raw(
                    'select id, avg(' + target + ') as avg, min(' + target + ') as min, max(' + target + ') as max, strftime("%Y-%W", date) as week from app_weather where date <= "' + to_date + '" and date >= "' + from_date + '" and area = "' + area + '" group by week'
                )

                response = []

                for index, item in enumerate(queryset):
                    if item.week[5:] == '00':
                        continue

                    if index == 0:
                        from_dt = from_date
                        to_dt = (datetime.datetime.strptime(item.week + '-1', "%Y-%W-%w") + timedelta(days=6)).strftime("%Y-%m-%d")
                    elif index == len(queryset) - 1:
                        from_dt = datetime.datetime.strptime(item.week + '-1', "%Y-%W-%w").strftime("%Y-%m-%d")
                        to_dt = to_date
                    else:
                        from_dt = datetime.datetime.strptime(item.week + '-1', "%Y-%W-%w").strftime("%Y-%m-%d")
                        to_dt = (datetime.datetime.strptime(item.week + '-1', "%Y-%W-%w") + timedelta(days=6)).strftime("%Y-%m-%d")

                    serializer = ResponseSerializer(
                        data={
                            'from': from_dt,
                            'to': to_dt,
                            'period': period,
                            'target': target,
                            'area': area,
                            'value': {
                                'average': round(item.avg, 2), 
                                'min': item.min,
                                'max': item.max,
                            } 
                        }
                    )

                    response.append(serializer.initial_data)

                return Response(response)
            elif (period == 'monthly'):
                queryset = Weather.objects.raw(
                    'select id, avg(' + target + ') as avg, min(' + target + ') as min, max(' + target + ') as max, strftime("%Y-%m", date) as month from app_weather where date <= "' + to_date + '" and date >= "' + from_date + '" and area = "' + area + '" group by month'
                )

                response = []

                for index, item in enumerate(queryset):
                    dt = item.month + '-01'

                    if index == 0:
                        to_date = self.get_last_date(datetime.date(int(from_date[0:4]), int(from_date[5:7]), int(from_date[8:10])))
                    elif index == len(queryset) - 1:
                        from_date = datetime.date(int(dt[0:4]), int(dt[5:7]), int(dt[8:10])).replace(day=1)
                    else:
                        from_date = datetime.date(int(dt[0:4]), int(dt[5:7]), int(dt[8:10])).replace(day=1)
                        to_date = self.get_last_date(datetime.date(int(from_date[0:4]), int(from_date[5:7]), int(from_date[8:10])))

                    serializer = ResponseSerializer(
                        data={
                            'from': from_dt,
                            'to': to_dt,
                            'period': period,
                            'target': target,
                            'area': area,
                            'value': {
                                'average': round(item.avg, 2), 
                                'min': item.min,
                                'max': item.max,
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