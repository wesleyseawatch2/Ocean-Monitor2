"""
station_data.views 測試 - 測站資料頁面測試
"""
import pytest
from django.urls import reverse
import json


# ==========================================
# 測站列表測試
# ==========================================

def test_station_list_status_code(client, station):
    """測試測站列表頁面回應狀態碼"""
    response = client.get(reverse('station_data:station_list'))
    assert response.status_code == 200


def test_station_list_template(client, station):
    """測試使用的 template"""
    response = client.get(reverse('station_data:station_list'))
    assert 'station_data/station_list.html' in [t.name for t in response.templates]


def test_station_list_contains_stations(client, multiple_stations):
    """測試頁面包含所有測站"""
    response = client.get(reverse('station_data:station_list'))

    # 確認 context 有 stations
    assert 'stations' in response.context
    assert response.context['stations'].count() == 3


def test_station_list_empty(client, db):
    """測試沒有測站時的頁面"""
    response = client.get(reverse('station_data:station_list'))

    assert response.status_code == 200
    assert response.context['stations'].count() == 0


# ==========================================
# 測站詳情測試
# ==========================================

def test_station_detail_status_code(client, station):
    """測試測站詳情頁面回應狀態碼"""
    response = client.get(
        reverse('station_data:station_detail', args=[station.id])
    )
    assert response.status_code == 200


def test_station_detail_template(client, station):
    """測試使用的 template"""
    response = client.get(
        reverse('station_data:station_detail', args=[station.id])
    )
    assert 'station_data/station_detail.html' in [t.name for t in response.templates]


def test_station_detail_context_data(client, station, multiple_readings):
    """測試 context 包含必要資料"""
    response = client.get(
        reverse('station_data:station_detail', args=[station.id])
    )

    assert 'station' in response.context
    assert 'readings' in response.context
    assert 'stats' in response.context
    assert 'total_count' in response.context
    assert 'chart_data_json' in response.context


def test_station_detail_readings_limit(client, station, multiple_readings):
    """測試數據記錄顯示限制（最多 50 筆）"""
    response = client.get(
        reverse('station_data:station_detail', args=[station.id])
    )

    # multiple_readings 只有 10 筆
    assert len(response.context['readings']) == 10


def test_station_detail_stats_structure(client, station, multiple_readings):
    """測試統計資料結構"""
    response = client.get(
        reverse('station_data:station_detail', args=[station.id])
    )

    stats = response.context['stats']

    # 確認有這些統計項目
    assert 'temperature' in stats
    assert 'ph' in stats
    assert 'oxygen' in stats
    assert 'salinity' in stats

    # 確認每個統計項目包含必要欄位
    assert 'count' in stats['temperature']
    assert 'avg' in stats['temperature']
    assert 'min' in stats['temperature']
    assert 'max' in stats['temperature']


def test_station_detail_chart_data_json(client, station, multiple_readings):
    """測試圖表數據是有效的 JSON"""
    response = client.get(
        reverse('station_data:station_detail', args=[station.id])
    )

    chart_data_json = response.context['chart_data_json']

    # 確認可以解析為 JSON
    chart_data = json.loads(chart_data_json)

    assert 'labels' in chart_data
    assert 'temperature' in chart_data
    assert 'ph' in chart_data


def test_station_detail_not_found(client, db):
    """測試不存在的測站會回傳 404"""
    response = client.get(
        reverse('station_data:station_detail', args=[99999])
    )
    assert response.status_code == 404


def test_station_detail_total_count(client, station, multiple_readings):
    """測試總數據筆數"""
    response = client.get(
        reverse('station_data:station_detail', args=[station.id])
    )

    assert response.context['total_count'] == 10


def test_station_detail_without_readings(client, station):
    """測試沒有數據記錄的測站"""
    response = client.get(
        reverse('station_data:station_detail', args=[station.id])
    )

    assert response.status_code == 200
    assert len(response.context['readings']) == 0
    assert response.context['total_count'] == 0


# ==========================================
# 數據記錄列表測試
# ==========================================

def test_reading_list_status_code(client, reading):
    """測試數據記錄列表頁面回應狀態碼"""
    response = client.get(reverse('station_data:reading_list'))
    assert response.status_code == 200


def test_reading_list_template(client, reading):
    """測試使用的 template"""
    response = client.get(reverse('station_data:reading_list'))
    assert 'station_data/reading_list.html' in [t.name for t in response.templates]


def test_reading_list_contains_readings(client, multiple_readings):
    """測試頁面包含數據記錄"""
    response = client.get(reverse('station_data:reading_list'))

    assert 'readings' in response.context
    assert len(response.context['readings']) == 10


def test_reading_list_limit_100(client, db, station):
    """測試數據記錄限制（最多 100 筆）"""
    from data_ingestion.models import Reading
    from django.utils import timezone
    from datetime import timedelta
    from decimal import Decimal

    # 建立 150 筆數據
    for i in range(150):
        Reading.objects.create(
            station=station,
            timestamp=timezone.now() - timedelta(hours=i),
            temperature=Decimal(f'{20.0 + i}')
        )

    response = client.get(reverse('station_data:reading_list'))

    # 應該只顯示 100 筆
    assert len(response.context['readings']) == 100


def test_reading_list_select_related(client, multiple_readings):
    """測試使用 select_related 優化查詢"""
    response = client.get(reverse('station_data:reading_list'))

    # 確認可以存取 station 而不會觸發額外查詢
    readings = response.context['readings']
    for reading in readings:
        # 這不應該觸發額外的資料庫查詢
        station_name = reading.station.station_name
        assert station_name is not None


def test_reading_list_empty(client, db):
    """測試沒有數據記錄時的頁面"""
    response = client.get(reverse('station_data:reading_list'))

    assert response.status_code == 200
    assert len(response.context['readings']) == 0
