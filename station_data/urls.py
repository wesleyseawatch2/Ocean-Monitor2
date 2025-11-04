from django.urls import path
from . import views

app_name = 'station_data'

urlpatterns = [
    path('', views.station_list, name='station_list'),
    path('stations/<int:station_id>/', views.station_detail, name='station_detail'),
    path('readings/', views.reading_list, name='reading_list'),
]
