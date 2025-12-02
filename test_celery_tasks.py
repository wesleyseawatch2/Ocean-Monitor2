"""
測試 Celery 定時任務

使用方式：
python test_celery_tasks.py
"""
import os
import django

# 設定 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from station_data.tasks import (
    update_ocean_data_from_source,
    check_ocean_data_alerts,
    generate_daily_statistics
)


def test_update_ocean_data():
    """測試更新海洋數據任務"""
    print("=" * 60)
    print("測試：更新海洋數據")
    print("=" * 60)

    result = update_ocean_data_from_source()

    print(f"\n狀態: {result['status']}")
    if result['status'] == 'success':
        print(f"測站: {result['station']}")
        print(f"數據 ID: {result['reading_id']}")
        print(f"時間戳: {result['timestamp']}")
    elif result['status'] == 'skipped':
        print(f"原因: {result['reason']}")

    print("\n[OK] 測試完成")


def test_check_alerts():
    """測試檢查數據異常任務"""
    print("\n" + "=" * 60)
    print("測試：檢查數據異常")
    print("=" * 60)

    result = check_ocean_data_alerts()

    print(f"\n狀態: {result['status']}")
    print(f"警告數量: {result['alerts_count']}")

    if result['alerts']:
        print("\n警告列表:")
        for i, alert in enumerate(result['alerts'], 1):
            print(f"  {i}. {alert}")
    else:
        print("\n無異常數據")

    print("\n[OK] 測試完成")


def test_daily_statistics():
    """測試每日統計報告任務"""
    print("\n" + "=" * 60)
    print("測試：每日統計報告")
    print("=" * 60)

    result = generate_daily_statistics()

    print(f"\n狀態: {result['status']}")
    print(f"日期: {result['date']}")
    print(f"今日數據筆數: {result['total_readings']}")

    print("\n各測站統計:")
    for stat in result['station_stats']:
        print(f"  - {stat['station_name']}: {stat['today_count']} 筆")

    print("\n平均值:")
    avg = result['averages']
    if avg['avg_temperature']:
        print(f"  - 平均溫度: {avg['avg_temperature']:.2f}°C")
    if avg['avg_salinity']:
        print(f"  - 平均鹽度: {avg['avg_salinity']:.2f} PSU")
    if avg['avg_ph']:
        print(f"  - 平均 pH: {avg['avg_ph']:.2f}")
    if avg['avg_oxygen']:
        print(f"  - 平均溶氧: {avg['avg_oxygen']:.2f} mg/L")

    print("\n[OK] 測試完成")


if __name__ == '__main__':
    print("\n=== 海洋監測系統 - Celery 任務測試 ===")
    print("=" * 60)

    try:
        # 測試 1: 更新海洋數據
        test_update_ocean_data()

        # 測試 2: 檢查數據異常
        test_check_alerts()

        # 測試 3: 每日統計報告
        test_daily_statistics()

        print("\n" + "=" * 60)
        print("[OK] 所有測試完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] 測試失敗: {e}")
        import traceback
        traceback.print_exc()
