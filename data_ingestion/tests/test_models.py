"""
Station 和 Reading Model 測試 - pytest 風格
"""
import pytest
from data_ingestion.models import Station, Reading
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal


# ==========================================
# Station 測試
# ==========================================

def test_station_creation(station):
    """測試測站建立"""
    assert station.station_name == '測試測站A'
    assert station.device_model == 'Model-X100'
    assert station.location == '台北港'
    assert str(station.install_date) == '2024-01-15'


def test_station_str_method(station):
    """測試 __str__ 方法"""
    assert str(station) == '測試測站A (台北港)'


def test_create_multiple_stations(multiple_stations):
    """測試建立多個測站"""
    assert len(multiple_stations) == 3
    assert Station.objects.count() == 3


def test_station_queryset_filtering(multiple_stations):
    """測試測站查詢與篩選"""
    # 按名稱篩選
    station_a = Station.objects.filter(station_name='測站A')
    assert station_a.count() == 1
    assert station_a.first().location == '台北港'

    # 按地點篩選
    kaohsiung_stations = Station.objects.filter(location__contains='高雄')
    assert kaohsiung_stations.count() == 1


# ==========================================
# Reading 測試
# ==========================================

def test_reading_creation(reading):
    """測試數據記錄建立"""
    assert reading.station.station_name == '測試測站A'
    assert reading.temperature == Decimal('25.5')
    assert reading.ph == Decimal('8.20')
    assert reading.oxygen == Decimal('7.500')
    assert reading.salinity == Decimal('35.1234')


def test_reading_str_method(reading):
    """測試 __str__ 方法"""
    result = str(reading)
    assert '測試測站A' in result
    assert reading.timestamp.strftime('%Y-%m-%d') in result


def test_reading_with_null_values(db, station):
    """測試允許 NULL 值的欄位"""
    reading = Reading.objects.create(
        station=station,
        timestamp=timezone.now(),
        temperature=None,  # 允許為 None
        ph=None,
        oxygen=None,
        salinity=None
    )

    assert reading.temperature is None
    assert reading.ph is None


def test_reading_foreign_key_relationship(reading, station):
    """測試 Reading 與 Station 的外鍵關係"""
    # 從 Reading 取得 Station
    assert reading.station == station

    # 從 Station 取得相關的 Readings (透過 related_name='readings')
    assert station.readings.count() == 1
    assert station.readings.first() == reading


def test_station_cascade_delete(db, station):
    """測試刪除測站時會連帶刪除數據記錄"""
    # 建立 3 筆數據
    for i in range(3):
        Reading.objects.create(
            station=station,
            timestamp=timezone.now() - timedelta(hours=i),
            temperature=Decimal(f'{25.0 + i}')
        )

    assert station.readings.count() == 3

    # 刪除測站
    station.delete()

    # 確認數據記錄也被刪除
    assert Reading.objects.count() == 0


# ==========================================
# Reading 排序測試
# ==========================================

def test_reading_default_ordering(multiple_readings):
    """測試預設排序（應該按時間倒序）"""
    readings = Reading.objects.all()

    # 第一筆應該是最新的
    assert readings.first().timestamp > readings.last().timestamp


def test_reading_queryset_filtering(multiple_readings, station):
    """測試數據查詢與篩選"""
    # 篩選溫度大於 25 的數據
    hot_readings = Reading.objects.filter(temperature__gt=25)
    assert hot_readings.count() > 0

    # 篩選特定測站的數據
    station_readings = Reading.objects.filter(station=station)
    assert station_readings.count() == 10


# ==========================================
# 數據統計測試
# ==========================================

def test_station_reading_count(station, multiple_readings):
    """測試測站的數據筆數"""
    assert station.readings.count() == 10


def test_reading_time_range_query(db, station):
    """測試時間範圍查詢"""
    now = timezone.now()

    # 建立不同時間的數據
    Reading.objects.create(
        station=station,
        timestamp=now - timedelta(days=1),
        temperature=Decimal('20.0')
    )
    Reading.objects.create(
        station=station,
        timestamp=now - timedelta(days=7),
        temperature=Decimal('21.0')
    )
    Reading.objects.create(
        station=station,
        timestamp=now - timedelta(days=30),
        temperature=Decimal('22.0')
    )

    # 查詢近 7 天的數據（包含 7 天前當天）
    week_ago = now - timedelta(days=7)
    recent_readings = Reading.objects.filter(timestamp__gte=week_ago)

    # 應該包含 1 天前和 7 天前的數據，共 2 筆
    assert recent_readings.count() == 2


# ==========================================
# Decimal 精度測試
# ==========================================

def test_reading_decimal_precision(db, station):
    """測試數值欄位的小數精度"""
    reading = Reading.objects.create(
        station=station,
        timestamp=timezone.now(),
        temperature=Decimal('25.55'),  # 2 位小數
        salinity=Decimal('35.1234'),   # 4 位小數
        pressure=Decimal('10.123')     # 3 位小數
    )

    # 從資料庫重新讀取
    reading.refresh_from_db()

    assert reading.temperature == Decimal('25.55')
    assert reading.salinity == Decimal('35.1234')
    assert reading.pressure == Decimal('10.123')
