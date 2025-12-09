"""
calculations.py 函數測試 - pytest 風格
"""
import pytest
from analysis_tools.calculations import (
    calculate_average,
    calculate_min_max,
    calculate_statistics
)
from decimal import Decimal


# ==========================================
# calculate_average 測試
# ==========================================

def test_calculate_average_with_integers():
    """測試整數平均值計算"""
    values = [10, 20, 30, 40, 50]
    result = calculate_average(values)
    assert result == 30


def test_calculate_average_with_floats():
    """測試浮點數平均值計算"""
    values = [1.5, 2.5, 3.5]
    result = calculate_average(values)
    assert result == 2.5


def test_calculate_average_with_empty_list():
    """測試空陣列應回傳 None"""
    values = []
    result = calculate_average(values)
    assert result is None


def test_calculate_average_with_single_value():
    """測試單一值的平均"""
    values = [42]
    result = calculate_average(values)
    assert result == 42


# ==========================================
# calculate_min_max 測試
# ==========================================

def test_calculate_min_max_basic():
    """測試基本最小最大值計算"""
    values = [5, 2, 8, 1, 9, 3]
    min_val, max_val = calculate_min_max(values)
    assert min_val == 1
    assert max_val == 9


def test_calculate_min_max_with_negative():
    """測試包含負數的情況"""
    values = [-10, -5, 0, 5, 10]
    min_val, max_val = calculate_min_max(values)
    assert min_val == -10
    assert max_val == 10


def test_calculate_min_max_with_empty_list():
    """測試空陣列應回傳 (None, None)"""
    values = []
    min_val, max_val = calculate_min_max(values)
    assert min_val is None
    assert max_val is None


def test_calculate_min_max_with_single_value():
    """測試單一值時，最小和最大值相同"""
    values = [42]
    min_val, max_val = calculate_min_max(values)
    assert min_val == 42
    assert max_val == 42


def test_calculate_min_max_with_decimals():
    """測試 Decimal 類型的最小最大值"""
    values = [Decimal('1.5'), Decimal('2.8'), Decimal('0.3')]
    min_val, max_val = calculate_min_max(values)
    assert min_val == Decimal('0.3')
    assert max_val == Decimal('2.8')


# ==========================================
# calculate_statistics 測試（整合測試）
# ==========================================

def test_calculate_statistics_basic(multiple_readings):
    """測試基本統計資料計算"""
    stats = calculate_statistics(multiple_readings, 'temperature')

    assert stats['count'] == 10
    assert stats['avg'] is not None
    assert stats['min'] is not None
    assert stats['max'] is not None


def test_calculate_statistics_with_actual_values(multiple_readings):
    """測試統計值的正確性（已知數據）"""
    stats = calculate_statistics(multiple_readings, 'temperature')

    # multiple_readings 溫度範圍是 20.0 ~ 29.0
    assert stats['count'] == 10
    assert stats['min'] == Decimal('20.0')
    assert stats['max'] == Decimal('29.0')
    assert stats['avg'] == 24.50  # (20+21+...+29) / 10 = 24.5


def test_calculate_statistics_with_null_values(readings_with_null_values):
    """測試包含 NULL 值的統計計算（應該跳過 None）"""
    stats = calculate_statistics(readings_with_null_values, 'temperature')

    # 只有一筆有 temperature 值
    assert stats['count'] == 1
    assert stats['avg'] == 25.0


def test_calculate_statistics_all_null_values(readings_with_null_values):
    """測試全部都是 NULL 的欄位"""
    stats = calculate_statistics(readings_with_null_values, 'ph')

    # 有一筆 pH 值是 8.0，另一筆是 None
    assert stats['count'] == 1
    assert stats['avg'] == 8.0


def test_calculate_statistics_empty_readings(db, station):
    """測試沒有任何數據時的統計"""
    empty_readings = station.readings.all()  # 沒有建立任何 reading

    stats = calculate_statistics(empty_readings, 'temperature')

    assert stats['count'] == 0
    assert stats['avg'] is None
    assert stats['min'] is None
    assert stats['max'] is None


def test_calculate_statistics_ph_field(multiple_readings):
    """測試 pH 欄位的統計"""
    stats = calculate_statistics(multiple_readings, 'ph')

    # pH 範圍是 7.0 ~ 7.9
    assert stats['count'] == 10
    assert stats['min'] == Decimal('7.0')
    assert stats['max'] == Decimal('7.9')


def test_calculate_statistics_rounding(db, station):
    """測試平均值會四捨五入到小數點後 2 位"""
    from data_ingestion.models import Reading
    from django.utils import timezone

    # 建立溫度值：10, 11, 12（平均 11.0）
    for temp in [10, 11, 12]:
        Reading.objects.create(
            station=station,
            timestamp=timezone.now(),
            temperature=Decimal(str(temp))
        )

    readings = station.readings.all()
    stats = calculate_statistics(readings, 'temperature')

    assert stats['avg'] == 11.0


def test_calculate_statistics_complex_average(db, station):
    """測試較複雜的平均值計算（會產生無窮小數）"""
    from data_ingestion.models import Reading
    from django.utils import timezone

    # 建立溫度值：10, 11, 12（平均 11.0）
    for temp in [10, 15, 20]:
        Reading.objects.create(
            station=station,
            timestamp=timezone.now(),
            temperature=Decimal(str(temp))
        )

    readings = station.readings.all()
    stats = calculate_statistics(readings, 'temperature')

    # (10 + 15 + 20) / 3 = 15.0
    assert stats['avg'] == 15.0
