#ocean_monitor\station_data\urls.py
from django.urls import path
from . import views

app_name = 'station_data'

urlpatterns = [
    path('', views.station_list, name='station_list'),
    path('<int:station_id>/', views.station_detail, name='station_detail'),
    path('<int:station_id>/realtime/', views.station_detail_realtime, name='station_detail_realtime'),
    path('<int:station_id>/chart-data/', views.get_chart_data_ajax, name='get_chart_data_ajax'),
    path('readings/', views.reading_list, name='reading_list'),

    # 報告相關路由
    path('reports/', views.report_list, name='report_list'),
    path('reports/<int:report_id>/', views.report_detail, name='report_detail'),
    path('reports/<int:report_id>/delete/', views.report_delete, name='report_delete'),
    path('reports/delete-all/', views.report_delete_all, name='report_delete_all'),
    path('reports/<int:report_id>/insight/', views.report_insight, name='report_insight'),
]
