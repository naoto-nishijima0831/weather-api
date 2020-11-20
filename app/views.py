import django_filters

import datetime
import calendar

from datetime import timedelta

from rest_framework import viewsets, filters, status
from rest_framework.response import Response


from .models import Weather
from .serializer import ResponseSerializer

from django.shortcuts import render
from django.db.models import Count, Avg, Max, Min


def login(request):
    return render(request, 'app/login.html', {})


def weather(request):
    return render(request, 'app/weather.html', {})


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

            from_date = self.get_from_date_or_to_date(area, 'from', from_date)
            to_date = self.get_from_date_or_to_date(area, 'to', to_date)
            
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
                    res_from_date = item['date']
                    res_to_date = item['date']
                elif period == 'weekly':
                    if item['date'][5:] == '00':
                        continue

                    first_day_of_the_week = datetime.datetime.strptime(item['date'] + '-1', "%Y-%W-%w")

                    if index == 0:
                        res_from_date = from_date
                        res_to_date = (first_day_of_the_week + timedelta(days=6)).strftime("%Y-%m-%d")
                    elif index == len(queryset) - 1:
                        res_from_date = first_day_of_the_week.strftime("%Y-%m-%d")
                        res_to_date = to_date
                    else:
                        res_from_date = first_day_of_the_week.strftime("%Y-%m-%d")
                        res_to_date = (first_day_of_the_week + timedelta(days=6)).strftime("%Y-%m-%d")
                elif period == 'monthly':
                    first_day_of_the_month = datetime.date(int((item['date'] + '-01')[0:4]), int((item['date'] + '-01')[5:7]), int((item['date'] + '-01')[8:10])).replace(day=1)

                    if index == 0:
                        res_from_date = from_date
                        res_to_date = self.get_last_date(res_from_date)
                    elif index == len(queryset) - 1:
                        res_from_date = first_day_of_the_month
                        res_to_date = to_date
                    else:
                        res_from_date = first_day_of_the_month
                        res_to_date = self.get_last_date(res_from_date)

                serializer = ResponseSerializer(
                    data={
                        'from_date': res_from_date, 
                        'to_date': res_to_date, 
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

    def get_from_date_or_to_date(self, area, from_or_to, date):
        if from_or_to == 'from':
            the_oldest_date_in_table = Weather.objects.filter(area=area).order_by('date').first().date
            response_date = the_oldest_date_in_table if the_oldest_date_in_table > date else date
        elif from_or_to == 'to':
            the_latest_date_in_table = Weather.objects.filter(area=area).order_by('date').reverse().first().date
            response_date = the_latest_date_in_table if the_latest_date_in_table < date else date
        return response_date