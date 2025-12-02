from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # 登出
    path('logout/', views.admin_logout, name='logout'),

    # 儀表板
    path('', views.dashboard, name='dashboard'),

    # 測站管理
    path('stations/', views.station_list, name='station_list'),
    path('stations/create/', views.station_create, name='station_create'),
    path('stations/<int:pk>/edit/', views.station_edit, name='station_edit'),
    path('stations/<int:pk>/delete/', views.station_delete, name='station_delete'),

    # 數據記錄
    path('readings/', views.reading_list, name='reading_list'),

    # 使用者管理
    path('users/', views.user_list, name='user_list'),

    # 定時任務管理
    path('periodic-tasks/', views.periodic_task_list, name='periodic_task_list'),
    path('periodic-tasks/create/', views.periodic_task_create, name='periodic_task_create'),
    path('periodic-tasks/<int:pk>/edit/', views.periodic_task_edit, name='periodic_task_edit'),
    path('periodic-tasks/<int:pk>/delete/', views.periodic_task_delete, name='periodic_task_delete'),
    path('periodic-tasks/<int:pk>/toggle/', views.periodic_task_toggle, name='periodic_task_toggle'),
]
