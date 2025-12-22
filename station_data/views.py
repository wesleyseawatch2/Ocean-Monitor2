#ocean_monitor\station_data\views.py
import json
from django.shortcuts import render, get_object_or_404
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.http import condition
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from data_ingestion.models import Station, Reading
from station_data.models import Report
from analysis_tools.calculations import calculate_statistics
from analysis_tools.chart_helpers import prepare_chart_data
import time


@login_required
def station_list(request):
    stations = Station.objects.all()
    context = {'stations': stations}
    return render(request, 'station_data/station_list.html', context)


@login_required
def station_detail(request, station_id):
    from django.utils import timezone
    from datetime import timedelta

    station = get_object_or_404(Station, pk=station_id)

    # 獲取時間範圍參數 (默認為最近 24 小時)
    time_range = request.GET.get('time_range', '24h')

    # 根據時間範圍計算起始時間
    now = timezone.now()
    time_ranges = {
        '1h': timedelta(hours=1),
        '6h': timedelta(hours=6),
        '12h': timedelta(hours=12),
        '24h': timedelta(hours=24),
        '3d': timedelta(days=3),
        '7d': timedelta(days=7),
        '30d': timedelta(days=30),
        'all': None,
    }

    time_delta = time_ranges.get(time_range, timedelta(hours=24))

    # 獲取數據
    if time_delta:
        start_time = now - time_delta
        all_readings = station.readings.filter(timestamp__gte=start_time).order_by('-timestamp')
    else:
        all_readings = station.readings.all().order_by('-timestamp')

    # 表格顯示最新 50 筆
    readings = all_readings[:50]

    # 圖表使用篩選後的所有數據
    chart_readings = all_readings[:200]  # 限制最多 200 筆避免圖表過於擁擠

    stats = {
        'temperature': calculate_statistics(readings, 'temperature'),
        'ph': calculate_statistics(readings, 'ph'),
        'oxygen': calculate_statistics(readings, 'oxygen'),
        'salinity': calculate_statistics(readings, 'salinity'),
    }

    chart_data = prepare_chart_data(chart_readings)

    # 獲取該測站的 GPS 軌跡數據（最新 100 筆）
    latest_gps_readings = station.readings.filter(
        latitude__isnull=False,
        longitude__isnull=False
    ).order_by('-timestamp')[:100]

    # 按時間順序排序以正確顯示軌跡（從舊到新）
    gps_points = []
    for reading in reversed(list(latest_gps_readings)):
        gps_points.append({
            'station_name': station.station_name,
            'latitude': float(reading.latitude),
            'longitude': float(reading.longitude),
            'timestamp': reading.timestamp.isoformat(),
            'temperature': float(reading.temperature) if reading.temperature else None,
            'ph': float(reading.ph) if reading.ph else None,
            'oxygen': float(reading.oxygen) if reading.oxygen else None,
        })

    # 獲取該測站最新的 100 筆數據記錄
    latest_readings = station.readings.order_by('-timestamp')[:100]

    context = {
        'station': station,
        'readings': readings,
        'stats': stats,
        'total_count': station.readings.count(),
        'chart_data_json': json.dumps(chart_data),
        'time_range': time_range,
        'gps_points': gps_points,
        'gps_points_json': json.dumps(gps_points),
        'latest_readings': latest_readings,
    }
    return render(request, 'station_data/station_detail.html', context)


@login_required
def reading_list(request):
    """數據記錄列表 - 包含 GPS 軌跡地圖"""
    # 表格顯示最新 100 筆
    readings = Reading.objects.select_related('station').order_by('-timestamp')[:100]

    # 地圖只顯示最新 100 個 GPS 點（更清晰、載入更快）
    latest_gps_readings = Reading.objects.select_related('station').filter(
        latitude__isnull=False,
        longitude__isnull=False
    ).order_by('-timestamp')[:100]  # 最新 100 筆

    # 按時間順序排序以正確顯示軌跡（從舊到新）
    gps_points = []
    for reading in reversed(list(latest_gps_readings)):  # 反轉順序使最舊的在前
        gps_points.append({
            'station_name': reading.station.station_name,
            'latitude': float(reading.latitude),
            'longitude': float(reading.longitude),
            'timestamp': reading.timestamp.isoformat(),
            'temperature': float(reading.temperature) if reading.temperature else None,
            'ph': float(reading.ph) if reading.ph else None,
            'oxygen': float(reading.oxygen) if reading.oxygen else None,
        })

    context = {
        'readings': readings,
        'gps_points': gps_points,
        'gps_points_json': json.dumps(gps_points),
    }
    return render(request, 'station_data/reading_list.html', context)


@login_required
def get_chart_data_ajax(request, station_id):
    """AJAX 端點 - 獲取圖表數據"""
    from django.utils import timezone
    from datetime import timedelta
    from django.http import JsonResponse

    station = get_object_or_404(Station, pk=station_id)
    time_range = request.GET.get('time_range', '24h')

    # 時間範圍映射
    now = timezone.now()
    time_ranges = {
        '1h': timedelta(hours=1),
        '6h': timedelta(hours=6),
        '12h': timedelta(hours=12),
        '24h': timedelta(hours=24),
        '3d': timedelta(days=3),
        '7d': timedelta(days=7),
        '30d': timedelta(days=30),
        'all': None,
    }

    time_delta = time_ranges.get(time_range, timedelta(hours=24))

    # 獲取數據
    if time_delta:
        start_time = now - time_delta
        chart_readings = station.readings.filter(timestamp__gte=start_time).order_by('-timestamp')[:200]
    else:
        chart_readings = station.readings.all().order_by('-timestamp')[:200]

    # 準備圖表數據
    chart_data = prepare_chart_data(chart_readings)

    return JsonResponse({
        'status': 'success',
        'chart_data': chart_data,
        'time_range': time_range,
    })


@login_required
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


@login_required
def report_list(request):
    """報告列表頁面"""
    # 獲取查詢參數
    report_type = request.GET.get('type', '')

    # 基本查詢
    reports = Report.objects.all()

    # 根據類型過濾
    if report_type:
        reports = reports.filter(report_type=report_type)

    # 分頁
    paginator = Paginator(reports, 20)  # 每頁 20 個報告
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # 統計不同類型的報告數量
    report_stats = {
        'total': Report.objects.count(),
        'daily_statistics': Report.objects.filter(report_type='daily_statistics').count(),
        'data_update': Report.objects.filter(report_type='data_update').count(),
        'alert_check': Report.objects.filter(report_type='alert_check').count(),
        'custom': Report.objects.filter(report_type='custom').count(),
    }

    context = {
        'page_obj': page_obj,
        'report_stats': report_stats,
        'current_type': report_type,
        'report_types': Report.REPORT_TYPES,
    }
    return render(request, 'station_data/report_list.html', context)


@login_required
def report_detail(request, report_id):
    """報告詳情頁面"""
    report = get_object_or_404(Report, pk=report_id)

    context = {
        'report': report,
    }
    return render(request, 'station_data/report_detail.html', context)


@login_required
def report_delete(request, report_id):
    """刪除報告"""
    if request.method == 'POST':
        report = get_object_or_404(Report, pk=report_id)
        report.delete()
        return JsonResponse({'status': 'success', 'message': '報告已刪除'})
    return JsonResponse({'status': 'error', 'message': '無效的請求方法'}, status=400)


@login_required
def report_delete_all(request):
    """刪除所有報告"""
    if request.method == 'POST':
        count = Report.objects.count()
        Report.objects.all().delete()
        return JsonResponse({'status': 'success', 'message': f'已刪除 {count} 個報告'})
    return JsonResponse({'status': 'error', 'message': '無效的請求方法'}, status=400)


@login_required
def report_insight(request, report_id):
    """
    使用 Gemini AI 生成報告洞察

    注意: 此功能只能讀取報告數據,不能讀取完整的原始數據
    """
    if request.method == 'POST':
        try:
            from analysis_tools.gemini_service import get_gemini_service

            # 獲取報告
            report = get_object_or_404(Report, pk=report_id)

            # 獲取 Gemini 服務
            gemini_service = get_gemini_service()

            if not gemini_service:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Gemini API 未配置。請設置 GEMINI_API_KEY 環境變量。'
                }, status=500)

            # 獲取去識別化參數
            import json as json_module
            request_data = json_module.loads(request.body) if request.body else {}
            anonymize = request_data.get('anonymize', False)

            # 生成洞察（支持去識別化）
            insight = gemini_service.generate_report_insight(report, anonymize=anonymize)

            if insight['status'] == 'success':
                return JsonResponse({
                    'status': 'success',
                    'insight': insight['content'],
                    'report_id': report.id,
                    'anonymized': insight.get('anonymized', False),
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': f"生成洞察失敗: {insight.get('error', '未知錯誤')}"
                }, status=500)

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'發生錯誤: {str(e)}'
            }, status=500)

    return JsonResponse({'status': 'error', 'message': '無效的請求方法'}, status=400)