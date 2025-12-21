"""
自動設置三個示範測站並生成完整一週的軌跡數據
使用方法: python manage.py setup_demo_stations
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import random
from zoneinfo import ZoneInfo

from data_ingestion.models import Station, Reading


class Command(BaseCommand):
    help = '自動創建三個測站並生成完整一週的軌跡數據'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='清空現有的所有測站和數據',
        )

    def handle(self, *args, **options):
        # 設定台灣時區
        taipei_tz = ZoneInfo('Asia/Taipei')

        # 清空現有數據
        if options['clear']:
            reading_count = Reading.objects.count()
            station_count = Station.objects.count()
            Reading.objects.all().delete()
            Station.objects.all().delete()
            self.stdout.write(self.style.WARNING(
                f'已刪除 {station_count} 個測站和 {reading_count} 筆數據'
            ))

        # 定義三個海域範圍和對應的測站
        STATIONS_CONFIG = [
            {
                'name': 'ChaoJingCR1000X',
                'device_model': 'CR1000X',
                'location': '潮境公園外海',
                'install_date': datetime(2025, 1, 15, tzinfo=taipei_tz).date(),
                'sea_area': {
                    'name': '潮境公園外海',
                    'lat_range': (25.115, 25.170),
                    'lng_range': (121.833, 121.923)
                }
            },
            {
                'name': 'BiShaCR1000X',
                'device_model': 'CR1000X',
                'location': '碧砂漁港外海',
                'install_date': datetime(2025, 2, 1, tzinfo=taipei_tz).date(),
                'sea_area': {
                    'name': '碧砂漁港外海',
                    'lat_range': (25.116693, 25.170747),
                    'lng_range': (121.817556, 121.907124)
                }
            },
            {
                'name': 'ZhengBinCR1000X',
                'device_model': 'CR1000X',
                'location': '正濱漁港外海',
                'install_date': datetime(2025, 3, 10, tzinfo=taipei_tz).date(),
                'sea_area': {
                    'name': '正濱漁港外海',
                    'lat_range': (25.126682, 25.180736),
                    'lng_range': (121.801490, 121.891066)
                }
            }
        ]

        # 創建或更新測站
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('開始創建測站...'))
        self.stdout.write('=' * 60)

        created_stations = []
        for config in STATIONS_CONFIG:
            # 在海域範圍內隨機選擇起始座標
            lat_min, lat_max = config['sea_area']['lat_range']
            lng_min, lng_max = config['sea_area']['lng_range']

            latitude = Decimal(str(round(random.uniform(lat_min, lat_max), 6)))
            longitude = Decimal(str(round(random.uniform(lng_min, lng_max), 6)))

            # 創建或更新測站
            station, created = Station.objects.update_or_create(
                station_name=config['name'],
                defaults={
                    'device_model': config['device_model'],
                    'location': config['location'],
                    'install_date': config['install_date'],
                    'latitude': latitude,
                    'longitude': longitude,
                }
            )

            action = '新建' if created else '更新'
            self.stdout.write(self.style.SUCCESS(
                f'[{action}] {station.station_name}'
            ))
            self.stdout.write(f'  位置: {config["location"]}')
            self.stdout.write(f'  座標: {latitude}, {longitude}')
            self.stdout.write(f'  裝設日期: {config["install_date"]}')
            self.stdout.write('')

            created_stations.append({
                'station': station,
                'sea_area': config['sea_area']
            })

        # 生成完整一週的數據
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('開始生成一週完整數據...'))
        self.stdout.write('=' * 60)

        # 設定時間範圍：2025-12-14 到 2025-12-21（完整一週）
        start_date = datetime(2025, 12, 14, 0, 0, 0, tzinfo=taipei_tz)
        end_date = datetime(2025, 12, 21, 23, 59, 59, tzinfo=taipei_tz)
        interval = timedelta(minutes=10)

        self.stdout.write(f'\n時間範圍: {start_date.strftime("%Y-%m-%d %H:%M")} ~ {end_date.strftime("%Y-%m-%d %H:%M")}')
        self.stdout.write(f'數據間隔: {interval.total_seconds() / 60} 分鐘')
        self.stdout.write(f'測站數量: {len(created_stations)}\n')

        total_readings = 0

        for station_info in created_stations:
            station = station_info['station']
            sea_area = station_info['sea_area']

            self.stdout.write(f'\n處理測站: {station.station_name}')
            self.stdout.write(f'  海域: {sea_area["name"]}')

            LAT_MIN, LAT_MAX = sea_area['lat_range']
            LNG_MIN, LNG_MAX = sea_area['lng_range']

            station_readings = 0
            current_time = start_date

            # 初始化 GPS 位置（從測站基礎位置開始）
            current_lat = float(station.latitude)
            current_lng = float(station.longitude)

            # 模擬主要洋流方向（東北向，帶有隨機擾動）
            drift_direction_lat = random.uniform(0.00005, 0.00015)  # 主要向北漂移
            drift_direction_lng = random.uniform(0.00005, 0.00015)  # 主要向東漂移

            while current_time <= end_date:
                # 生成連貫的 GPS 漂移（模擬洋流帶動儀器緩慢移動）
                lat_drift = drift_direction_lat + random.uniform(-0.00005, 0.00005)
                lng_drift = drift_direction_lng + random.uniform(-0.00005, 0.00005)

                current_lat += lat_drift
                current_lng += lng_drift

                # 確保保持在該測站對應的海域範圍內
                if current_lat < LAT_MIN:
                    current_lat = LAT_MIN + 0.001
                    drift_direction_lat = abs(drift_direction_lat)
                elif current_lat > LAT_MAX:
                    current_lat = LAT_MAX - 0.001
                    drift_direction_lat = -abs(drift_direction_lat)

                if current_lng < LNG_MIN:
                    current_lng = LNG_MIN + 0.001
                    drift_direction_lng = abs(drift_direction_lng)
                elif current_lng > LNG_MAX:
                    current_lng = LNG_MAX - 0.001
                    drift_direction_lng = -abs(drift_direction_lng)

                # 偶爾改變漂移方向（模擬洋流變化）
                if random.random() < 0.05:  # 5% 機率改變方向
                    drift_direction_lat += random.uniform(-0.0001, 0.0001)
                    drift_direction_lng += random.uniform(-0.0001, 0.0001)

                # 生成環境數據（帶日週期變化）
                hour = current_time.hour
                import math
                diurnal = (math.sin((hour - 6) * math.pi / 12) + 1) / 2

                # 基礎參數（加入測站間的細微差異）
                station_offset = hash(station.station_name) % 10 / 10  # 0.0-0.9

                temperature = 25.0 + diurnal * 3.0 + random.uniform(-0.5, 0.5) + station_offset * 0.5
                salinity = 33.5 + random.uniform(-0.3, 0.3) + station_offset * 0.2
                oxygen = 8.0 + (1 - diurnal) * 1.5 + random.uniform(-0.3, 0.3)
                ph = 8.2 + random.uniform(-0.2, 0.2)
                conductivity = 54000.0 + random.uniform(-300, 300) + station_offset * 100
                pressure = 0.6 + random.uniform(-0.03, 0.03)
                fluorescence = 0.5 + diurnal * 0.8 + random.uniform(-0.1, 0.1)
                turbidity = random.uniform(3.0, 7.0) + station_offset

                # 創建數據記錄
                Reading.objects.create(
                    station=station,
                    timestamp=current_time,
                    latitude=Decimal(str(round(current_lat, 6))),
                    longitude=Decimal(str(round(current_lng, 6))),
                    temperature=Decimal(str(round(temperature, 2))),
                    salinity=Decimal(str(round(salinity, 4))),
                    oxygen=Decimal(str(round(max(oxygen, 4.0), 3))),
                    ph=Decimal(str(round(ph, 2))),
                    conductivity=Decimal(str(round(conductivity, 2))),
                    pressure=Decimal(str(round(pressure, 3))),
                    fluorescence=Decimal(str(round(max(fluorescence, 0.0), 3))),
                    turbidity=Decimal(str(round(turbidity, 3))),
                )

                station_readings += 1
                current_time += interval

            self.stdout.write(self.style.SUCCESS(f'  [OK] 已生成 {station_readings} 筆數據'))
            total_readings += station_readings

        # 總結
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS(f'[完成] 設置完成！'))
        self.stdout.write('=' * 60)
        self.stdout.write(f'\n測站總數: {len(created_stations)} 個')
        self.stdout.write(f'數據總數: {total_readings:,} 筆')
        self.stdout.write(f'平均每測站: {total_readings // len(created_stations):,} 筆')

        # 計算預期數量
        expected_per_station = int((end_date - start_date).total_seconds() / interval.total_seconds()) + 1
        self.stdout.write(f'預期每測站: {expected_per_station:,} 筆')

        self.stdout.write('\n' + self.style.SUCCESS('現在可以訪問 http://localhost:8000 查看結果！'))
