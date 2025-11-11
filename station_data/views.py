#ocean_monitor\station_data\views.py
import json
from django.shortcuts import render, get_object_or_404
from data_ingestion.models import Station, Reading
from analysis_tools.calculations import calculate_statistics
from analysis_tools.chart_helpers import prepare_chart_data


def station_list(request):
    stations = Station.objects.all()
    context = {'stations': stations}
    return render(request, 'station_data/station_list.html', context)


def station_detail(request, station_id):
    station = get_object_or_404(Station, pk=station_id)
    readings = station.readings.all()[:50]
    
    stats = {
        'temperature': calculate_statistics(readings, 'temperature'),
        'ph': calculate_statistics(readings, 'ph'),
        'oxygen': calculate_statistics(readings, 'oxygen'),
        'salinity': calculate_statistics(readings, 'salinity'),
    }
    
    chart_data = prepare_chart_data(readings)
    
    context = {
        'station': station,
        'readings': readings,
        'stats': stats,
        'total_count': station.readings.count(),
        'chart_data_json': json.dumps(chart_data),
    }
    return render(request, 'station_data/station_detail.html', context)


def reading_list(request):
    readings = Reading.objects.select_related('station').all()[:100]
    context = {'readings': readings}
    return render(request, 'station_data/reading_list.html', context)