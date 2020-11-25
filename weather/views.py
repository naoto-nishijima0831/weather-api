from django.shortcuts import render

import requests


def index(request):
    return render(request, 'weather/weather.html')

def api(request):
    params = {
                'from_date'    : request.POST.get('from-date'), 
                'to_date'      : request.POST.get('to-date'), 
                'target'       : request.POST.get('target'), 
                'area'         : request.POST.get('area'), 
                'period'       : request.POST.get('period'),
            }
    horizontal = ['January', 'February', 'March', 'April', 'May', 'June', 'July']
    result = requests.get('http://127.0.0.1:8000/weather/summary', params=params).json()
    return render(request, 'weather/weather.html', {
        'api_result': result,
        'horizontal'   : horizontal,
    })
