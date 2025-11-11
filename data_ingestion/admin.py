#ocean_monitor\data_ingestion\admin.py
from django.contrib import admin
from .models import Station, Reading


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ('station_name', 'device_model', 'location', 'install_date')
    search_fields = ('station_name', 'location')


@admin.register(Reading)
class ReadingAdmin(admin.ModelAdmin):
    list_display = ('station', 'timestamp', 'temperature', 'ph', 'oxygen', 'salinity')
    list_filter = ('station', 'timestamp')
    date_hierarchy = 'timestamp'