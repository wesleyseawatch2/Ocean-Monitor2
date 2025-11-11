# apps/core/urls.py

from django.urls import path
from . import views

app_name = 'apps.core'

urlpatterns = [
    path('', views.home, name='home'),
]
