from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),  # allauth 的所有 URLs
    path('', include('station_data.urls')),
    path('core/', include('apps.core.urls')),
]