#!/usr/bin/env python
"""
快速開始實時模擬功能的測試腳本

使用方法:
    python realtime_demo.py              # 生成 5 輪模擬數據
    python realtime_demo.py --count=10   # 生成 10 輪
    python realtime_demo.py --help       # 查看幫助
"""

import os
import sys
import django
import argparse
from datetime import datetime, timedelta

# 設置 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from data_ingestion.models import Station, Reading
from station_data.simulation import OceanDataSimulator, simulate_data_for_all_stations
from django.utils import timezone


def setup_demo():
    """準備演示環境"""
    print("🌊 海洋監測系統 - 實時模擬演示")
    print("=" * 50)
    
    # 檢查測站
    stations = Station.objects.all()
    if not stations.exists():
        print("\n❌ 未找到測站，正在建立...")
        station, created = Station.objects.get_or_create(
            station_name='ChaoJingCR1000X',
            defaults={
                'device_model': 'CR1000X',
                'location': '潮境漁港',
                'install_date': datetime(2024, 8, 1).date()
            }
        )
        print(f"✓ 已建立測站: {station.station_name}")
        stations = Station.objects.all()
    
    print(f"✓ 找到 {stations.count()} 個測站")
    for station in stations:
        count = station.readings.count()
        print(f"  - {station.station_name}: {count} 筆記錄")
    
    return stations


def demo_single_reading():
    """生成單個數據記錄的演示"""
    print("\n📡 單個數據記錄演示")
    print("-" * 50)
    
    simulator = OceanDataSimulator()
    station = Station.objects.first()
    
    if not station:
        print("❌ 沒有可用的測站")
        return
    
    print(f"生成中: {station.station_name}")
    reading = simulator.generate_reading(station)
    
    print(f"""
✓ 已生成新記錄 (ID: {reading.id})
  📅 時間: {reading.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
  🌡️  溫度: {reading.temperature}°C
  🧂 鹽度: {reading.salinity} PSU
  💧 溶氧: {reading.oxygen} mg/L
  📊 pH 值: {reading.ph}
  ⚡ 電導率: {reading.conductivity} µS/cm
  🔬 螢光值: {reading.fluorescence}
  🌫️  濁度: {reading.turbidity}
  🎯 壓力: {reading.pressure} bar
""")


def demo_batch_generation(count=5):
    """批量生成數據的演示"""
    print(f"\n📊 批量生成演示 ({count} 輪)")
    print("-" * 50)
    
    total_readings_before = Reading.objects.count()
    
    print(f"開始時間: {timezone.now().strftime('%H:%M:%S')}")
    print(f"初始記錄數: {total_readings_before}")
    
    for i in range(count):
        result = simulate_data_for_all_stations()
        
        if result['status'] == 'success':
            print(f"\n✓ [第 {i+1} 輪] 生成 {result['count']} 筆數據")
            for reading in result['readings']:
                print(f"    {reading['station_name']}: "
                      f"溫度={reading['temperature']}°C, "
                      f"鹽度={reading['salinity']}psu")
        else:
            print(f"✗ [第 {i+1} 輪] 失敗: {result['message']}")
    
    total_readings_after = Reading.objects.count()
    new_readings = total_readings_after - total_readings_before
    
    print(f"\n結束時間: {timezone.now().strftime('%H:%M:%S')}")
    print(f"新增記錄數: {new_readings}")
    print(f"總記錄數: {total_readings_after}")


def demo_statistics():
    """顯示統計數據的演示"""
    print("\n📈 數據統計演示")
    print("-" * 50)
    
    from analysis_tools.calculations import calculate_statistics
    
    station = Station.objects.first()
    if not station:
        print("❌ 沒有可用的測站")
        return
    
    # 先獲取 first 和 last，然後再進行切片
    all_readings = station.readings.all()
    
    if not all_readings.exists():
        print("❌ 沒有可用的數據記錄")
        return
    
    first_reading = all_readings.order_by('timestamp').first()
    last_reading = all_readings.order_by('-timestamp').first()
    
    readings = all_readings[:50]
    
    stats = {
        'temperature': calculate_statistics(readings, 'temperature'),
        'ph': calculate_statistics(readings, 'ph'),
        'oxygen': calculate_statistics(readings, 'oxygen'),
        'salinity': calculate_statistics(readings, 'salinity'),
    }
    
    print(f"\n站點: {station.station_name}")
    print(f"分析記錄數: {readings.count()}")
    print(f"時間範圍: {last_reading.timestamp.strftime('%Y-%m-%d %H:%M:%S')} ~ "
          f"{first_reading.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n溫度 (°C):")
    if stats['temperature']:
        print(f"  最小值: {stats['temperature']['min']}")
        print(f"  平均值: {stats['temperature']['avg']}")
        print(f"  最大值: {stats['temperature']['max']}")
    
    print("\nPH 值:")
    if stats['ph']:
        print(f"  最小值: {stats['ph']['min']}")
        print(f"  平均值: {stats['ph']['avg']}")
        print(f"  最大值: {stats['ph']['max']}")
    
    print("\n溶氧 (mg/L):")
    if stats['oxygen']:
        print(f"  最小值: {stats['oxygen']['min']}")
        print(f"  平均值: {stats['oxygen']['avg']}")
        print(f"  最大值: {stats['oxygen']['max']}")
    
    print("\n鹽度 (PSU):")
    if stats['salinity']:
        print(f"  最小值: {stats['salinity']['min']}")
        print(f"  平均值: {stats['salinity']['avg']}")
        print(f"  最大值: {stats['salinity']['max']}")


def demo_simulator_details():
    """展示模擬器的詳細參數"""
    print("\n⚙️  模擬器參數詳解")
    print("-" * 50)
    
    simulator = OceanDataSimulator()
    
    print(f"""
溫度 (Temperature):
  基礎值: {simulator.BASE_TEMP}°C
  波動範圍: ±{simulator.TEMP_AMPLITUDE}°C
  特點: 日週期變化，正午最高，午夜最低

鹽度 (Salinity):
  基礎值: {simulator.BASE_SALINITY} PSU
  波動範圍: ±{simulator.SALINITY_AMPLITUDE} PSU
  特點: 相對穩定，略有波動

溶氧 (Oxygen):
  基礎值: {simulator.BASE_OXYGEN} mg/L
  波動範圍: ±{simulator.OXYGEN_AMPLITUDE} mg/L
  特點: 與溫度反相關

pH 值:
  基礎值: {simulator.BASE_PH}
  波動範圍: ±{simulator.pH_AMPLITUDE}
  特點: 略有波動，保持海水正常範圍

電導率 (Conductivity):
  基礎值: {simulator.BASE_CONDUCTIVITY} µS/cm
  特點: 受鹽度影響

現在時間: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
當前小時: {timezone.now().hour} 點
日週期係數: {simulator.calculate_diurnal_factor():.2f} (0=午夜, 1=正午)
""")


def main():
    parser = argparse.ArgumentParser(
        description='🌊 海洋監測系統 - 實時模擬演示腳本'
    )
    
    parser.add_argument(
        '--count',
        type=int,
        default=5,
        help='批量生成的輪數（預設: 5）'
    )
    
    parser.add_argument(
        '--mode',
        choices=['full', 'single', 'batch', 'stats', 'params'],
        default='full',
        help='演示模式'
    )
    
    args = parser.parse_args()
    
    try:
        # 準備環境
        setup_demo()
        
        # 根據模式執行演示
        if args.mode in ['full', 'single']:
            demo_single_reading()
        
        if args.mode in ['full', 'batch']:
            demo_batch_generation(args.count)
        
        if args.mode in ['full', 'stats']:
            demo_statistics()
        
        if args.mode in ['full', 'params']:
            demo_simulator_details()
        
        print("\n" + "=" * 50)
        print("✅ 演示完成！")
        print("\n下一步:")
        print("1. 啟動 Django 開發伺服器:")
        print("   python manage.py runserver")
        print("\n2. 啟動 Celery Worker:")
        print("   celery -A config worker -l info")
        print("\n3. 啟動 Celery Beat:")
        print("   celery -A config beat -l info")
        print("\n4. 訪問網頁查看實時更新:")
        print("   http://localhost:8000/station_data/stations/1/")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ 錯誤: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
