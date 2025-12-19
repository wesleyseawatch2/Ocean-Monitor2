#ocean_monitor\station_data\views.py
import json
from django.shortcuts import render, get_object_or_404
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.http import condition
from django.core.paginator import Paginator
from data_ingestion.models import Station, Reading
from station_data.models import Report
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


def report_detail(request, report_id):
    """報告詳情頁面"""
    report = get_object_or_404(Report, pk=report_id)

    context = {
        'report': report,
    }
    return render(request, 'station_data/report_detail.html', context)


def report_delete(request, report_id):
    """刪除報告"""
    if request.method == 'POST':
        report = get_object_or_404(Report, pk=report_id)
        report.delete()
        return JsonResponse({'status': 'success', 'message': '報告已刪除'})
    return JsonResponse({'status': 'error', 'message': '無效的請求方法'}, status=400)


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

            # 生成洞察
            insight = gemini_service.generate_report_insight(report)

            if insight['status'] == 'success':
                return JsonResponse({
                    'status': 'success',
                    'insight': insight['content'],
                    'report_id': report.id,
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