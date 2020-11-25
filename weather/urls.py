from django.urls import path
from . import views

app_name ='weather'

urlpatterns =[
    path('', views.index, name='view'),
    path('api/', views.api, name='api'),
]