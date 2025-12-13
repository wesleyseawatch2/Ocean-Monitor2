#ocean_monitor\station_data\views.py
import json
from django.shortcuts import render, get_object_or_404
from django.http import StreamingHttpResponse
from django.views.decorators.http import condition
from data_ingestion.models import Station, Reading
from analysis_tools.calculations import calculate_statistics
from analysis_tools.chart_helpers import prepare_chart_data
import time


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


def station_detail_realtime(request, station_id):
    """
    實時推送站點數據的端點（使用 Server-Sent Events）
    
    前端可以使用 EventSource 連接此端點，接收實時數據更新
    """
    station = get_object_or_404(Station, pk=station_id)
    
    def event_stream():
        """生成實時數據流"""
        last_reading_id = None
        
        while True:
            try:
                # 每 5 秒檢查一次是否有新數據
                # 在生產環境中，你可能想增加檢查間隔
                time.sleep(5)
                
                # 獲取最新的數據記錄
                latest_reading = station.readings.order_by('-timestamp').first()
                
                # 如果有新數據，推送給客戶端
                if latest_reading and (last_reading_id is None or latest_reading.id != last_reading_id):
                    last_reading_id = latest_reading.id
                    
                    # 獲取統計數據
                    readings = station.readings.all()[:50]
                    stats = {
                        'temperature': calculate_statistics(readings, 'temperature'),
                        'ph': calculate_statistics(readings, 'ph'),
                        'oxygen': calculate_statistics(readings, 'oxygen'),
                        'salinity': calculate_statistics(readings, 'salinity'),
                    }
                    
                    # 準備圖表數據
                    chart_data = prepare_chart_data(readings)
                    
                    # 構造要發送的數據
                    data = {
                        'status': 'success',
                        'station_id': station.id,
                        'station_name': station.station_name,
                        'latest_reading': {
                            'id': latest_reading.id,
                            'timestamp': latest_reading.timestamp.isoformat(),
                            'temperature': float(latest_reading.temperature) if latest_reading.temperature else None,
                            'ph': float(latest_reading.ph) if latest_reading.ph else None,
                            'oxygen': float(latest_reading.oxygen) if latest_reading.oxygen else None,
                            'salinity': float(latest_reading.salinity) if latest_reading.salinity else None,
                            'conductivity': float(latest_reading.conductivity) if latest_reading.conductivity else None,
                            'pressure': float(latest_reading.pressure) if latest_reading.pressure else None,
                            'fluorescence': float(latest_reading.fluorescence) if latest_reading.fluorescence else None,
                            'turbidity': float(latest_reading.turbidity) if latest_reading.turbidity else None,
                        },
                        'stats': {
                            'temperature': stats['temperature'],
                            'ph': stats['ph'],
                            'oxygen': stats['oxygen'],
                            'salinity': stats['salinity'],
                        },
                        'chart_data': chart_data,
                        'total_count': station.readings.count(),
                    }
                    
                    # 以 SSE 格式發送數據
                    yield f"data: {json.dumps(data)}\n\n"
                    
            except Exception as e:
                # 發送錯誤信息
                error_data = {
                    'status': 'error',
                    'message': str(e)
                }
                yield f"data: {json.dumps(error_data)}\n\n"
                break
    
    # 返回 SSE 流響應
    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response