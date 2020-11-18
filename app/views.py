import django_filters

import datetime
import calendar

from datetime import timedelta

from rest_framework import viewsets, filters, status
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
                }, status=status.HTTP_400_BAD_REQUEST)

            if (period not in ['monthly', 'weekly', 'daily']):
                return Response({
                    'error' : {
                        'message' : '期間種別が不正です。'
                    }
                }, status=status.HTTP_400_BAD_REQUEST)

            if (target not in ['precipitation', 'daylight', 'windspeed']):
                return Response({
                    'error' : {
                        'message' : '集計対象が不正です。'
                    }
                }, status=status.HTTP_400_BAD_REQUEST)

            if (area not in ['Yokohama', 'Tokyo']):
                return Response({
                    'error' : {
                        'message' : '指定エリアが不正です。'
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if period == 'daily':
                dateFormat = '%Y-%m-%d'
            elif period == 'weekly':
                dateFormat = '%Y-%W'
            elif period == 'monthly':
                dateFormat = '%Y-%m'
            
            response = []
            queryset = Weather.objects.extra(select={'date':'strftime("' + dateFormat + '", date)'}, where=['area="' + area + '"and date>="' + str(from_date) + '" and date<="' + str(to_date) +'"']).values('date').annotate(avg=Avg(target), min=Min(target), max=Max(target))
            for index, item in enumerate(queryset):
                if period == 'daily':
                    from_dt = item['date']
                    to_dt = item['date']
                elif period == 'weekly':
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
                elif period == 'monthly':
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
                        'from_date': from_dt, 
                        'to_date': to_dt, 
                        'period': period,
                        'target': target,
                        'area': area,
                        'value': {
                            'average': round(item['avg'], 2), 
                            'min': round(item['min'], 2),
                            'max': round(item['max'], 2),
                        }
                    }
                )
                response.append(serializer.initial_data)
            return Response(response, status=status.HTTP_200_OK)
        except:
            return Response({
                'error' : {
                    'message' : 'サーバーエラーが発生しました。'
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_last_date(self, dt):
        return dt.replace(day=calendar.monthrange(dt.year, dt.month)[1])