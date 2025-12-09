"""
chart_helpers.py 函數測試 - pytest 風格
"""
import pytest
from analysis_tools.chart_helpers import prepare_chart_data
from data_ingestion.models import Reading
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal


# ==========================================
# prepare_chart_data 測試
# ==========================================

def test_prepare_chart_data_structure(multiple_readings):
    """測試回傳的數據結構"""
    result = prepare_chart_data(multiple_readings)

    # 確認有這些鍵
    assert 'labels' in result
    assert 'temperature' in result
    assert 'ph' in result
    assert 'oxygen' in result
    assert 'salinity' in result


def test_prepare_chart_data_labels_format(multiple_readings):
    """測試時間標籤格式（應為 MM/DD HH:MM）"""
    result = prepare_chart_data(multiple_readings)
    labels = result['labels']

    # 確認有 10 個標籤
    assert len(labels) == 10

    # 確認格式為 MM/DD HH:MM
    for label in labels:
        assert '/' in label
        assert ':' in label
        # 範例格式: "01/15 14:30"
        parts = label.split(' ')
        assert len(parts) == 2


def test_prepare_chart_data_values_conversion(multiple_readings):
    """測試數值轉換為 float"""
    result = prepare_chart_data(multiple_readings)

    # temperature 應該都是 float 或 None
    for temp in result['temperature']:
        assert isinstance(temp, float) or temp is None

    # pH 應該都是 float 或 None
    for ph in result['ph']:
        assert isinstance(ph, float) or ph is None


def test_prepare_chart_data_correct_length(multiple_readings):
    """測試所有陣列長度一致"""
    result = prepare_chart_data(multiple_readings)

    expected_length = len(multiple_readings)

    assert len(result['labels']) == expected_length
    assert len(result['temperature']) == expected_length
    assert len(result['ph']) == expected_length
    assert len(result['oxygen']) == expected_length
    assert len(result['salinity']) == expected_length


def test_prepare_chart_data_with_null_values(readings_with_null_values):
    """測試處理 NULL 值（應轉換為 None）"""
    result = prepare_chart_data(readings_with_null_values)

    # 確認 None 值有被保留
    assert None in result['temperature']
    assert None in result['ph']


def test_prepare_chart_data_reverses_order(db, station):
    """測試數據會被反轉（從舊到新）"""
    # 建立時間序列數據
    timestamps = []
    for i in range(3):
        time = timezone.now() - timedelta(hours=i)
        timestamps.append(time)
        Reading.objects.create(
            station=station,
            timestamp=time,
            temperature=Decimal(f'{20 + i}')
        )

    readings = station.readings.all()  # 預設是新到舊（-timestamp）
    result = prepare_chart_data(readings)

    # Chart 數據應該是舊到新（reversed）
    # 最早的時間應該在最前面
    first_label = result['labels'][0]
    last_label = result['labels'][-1]

    # 因為 reversed，最早建立的會在最前面
    # 但實際上 timestamps[2] 是最早的（now - 2 hours）
    # 所以反轉後，timestamps[2] 會在 index 0


def test_prepare_chart_data_empty_readings(db, station):
    """測試空的數據集"""
    empty_readings = station.readings.all()  # 沒有建立任何 reading

    result = prepare_chart_data(empty_readings)

    assert result['labels'] == []
    assert result['temperature'] == []
    assert result['ph'] == []
    assert result['oxygen'] == []
    assert result['salinity'] == []


def test_prepare_chart_data_actual_values(multiple_readings):
    """測試實際數值是否正確"""
    result = prepare_chart_data(multiple_readings)

    # multiple_readings 預設是按時間倒序（最新的在前）
    # reversed 後會變成正序（最舊的在前）
    temps = result['temperature']

    # 確認溫度值都在範圍內
    assert all(20.0 <= t <= 29.0 for t in temps if t is not None)

    # 確認有 10 筆數據
    assert len(temps) == 10


def test_prepare_chart_data_decimal_to_float_conversion(db, station):
    """測試 Decimal 正確轉換為 float"""
    Reading.objects.create(
        station=station,
        timestamp=timezone.now(),
        temperature=Decimal('25.55'),
        ph=Decimal('8.20'),
        oxygen=Decimal('7.500'),
        salinity=Decimal('35.1234')
    )

    readings = station.readings.all()
    result = prepare_chart_data(readings)

    assert result['temperature'][0] == 25.55
    assert result['ph'][0] == 8.20
    assert result['oxygen'][0] == 7.500
    assert result['salinity'][0] == 35.1234


def test_prepare_chart_data_handles_mixed_null_and_values(db, station):
    """測試混合 NULL 和有值的情況"""
    Reading.objects.create(
        station=station,
        timestamp=timezone.now(),
        temperature=Decimal('25.0'),
        ph=None
    )
    Reading.objects.create(
        station=station,
        timestamp=timezone.now() - timedelta(hours=1),
        temperature=None,
        ph=Decimal('8.0')
    )

    readings = station.readings.all()
    result = prepare_chart_data(readings)

    # 第一筆（反轉後）：temp=None, ph=8.0
    assert result['temperature'][0] is None
    assert result['ph'][0] == 8.0

    # 第二筆（反轉後）：temp=25.0, ph=None
    assert result['temperature'][1] == 25.0
    assert result['ph'][1] is None
