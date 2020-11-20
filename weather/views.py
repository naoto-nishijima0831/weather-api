from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'weather/weather.html')

def api(request):
    print(request.POST.get('from-date'))
    print(request.POST.get('to-date'))
    print(request.POST.get('target'))
    print(request.POST.get('area'))
    return render(request, 'weather/weather.html')
