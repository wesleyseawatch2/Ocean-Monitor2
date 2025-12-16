#ocean_monitor\station_data\urls.py
from django.urls import path
from . import views

app_name = 'station_data'

urlpatterns = [
    path('', views.station_list, name='station_list'),
    path('<int:station_id>/', views.station_detail, name='station_detail'),
    path('<int:station_id>/realtime/', views.station_detail_realtime, name='station_detail_realtime'),
    path('readings/', views.reading_list, name='reading_list'),
]
