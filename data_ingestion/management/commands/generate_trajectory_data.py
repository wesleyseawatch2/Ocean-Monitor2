"""
生成歷史軌跡數據
從 2025-12-14 到 2025-12-21，每 10 分鐘一筆記錄
使用方法: python manage.py generate_trajectory_data
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import random
from zoneinfo import ZoneInfo

from data_ingestion.models import Station, Reading


class Command(BaseCommand):
    help = '生成 12/14-12/21 的歷史軌跡數據（每10分鐘一筆）'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='清空現有的所有 Reading 數據',
        )

    def handle(self, *args, **options):
        # 設定台灣時區
        taipei_tz = ZoneInfo('Asia/Taipei')

        # 清空現有數據
        if options['clear']:
            count = Reading.objects.count()
            Reading.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'已刪除 {count} 筆舊數據'))

        # 獲取所有測站
        stations = Station.objects.all()

        if not stations.exists():
            self.stdout.write(self.style.ERROR('錯誤: 沒有找到任何測站!'))
            self.stdout.write('請先在管理後台創建測站')
            return

        # 定義三個海域範圍
        SEA_AREAS = {
            'chaojing': {  # 潮境公園外海
                'name': '潮境公園外海',
                'lat_range': (25.115, 25.170),
                'lng_range': (121.833, 121.923)
            },
            'bisha': {  # 碧砂漁港外海
                'name': '碧砂漁港外海',
                'lat_range': (25.116693, 25.170747),
                'lng_range': (121.817556, 121.907124)
            },
            'zhengbin': {  # 正濱漁港外海
                'name': '正濱漁港外海',
                'lat_range': (25.126682, 25.180736),
                'lng_range': (121.801490, 121.891066)
            }
        }

        # 自動為沒有經緯度的測站設置海上初始座標
        stations_updated = 0
        station_list = list(stations)

        for idx, station in enumerate(station_list):
            if not station.latitude or not station.longitude:
                # 根據測站索引循環分配海域
                area_keys = list(SEA_AREAS.keys())
                area_key = area_keys[idx % len(area_keys)]
                area = SEA_AREAS[area_key]

                # 在該海域範圍內隨機選擇起始點
                lat_min, lat_max = area['lat_range']
                lng_min, lng_max = area['lng_range']
                station.latitude = Decimal(str(round(random.uniform(lat_min, lat_max), 6)))
                station.longitude = Decimal(str(round(random.uniform(lng_min, lng_max), 6)))
                station.save()
                stations_updated += 1
                self.stdout.write(self.style.SUCCESS(
                    f'已為測站 "{station.station_name}" 設置 {area["name"]} 座標: '
                    f'{station.latitude}°N, {station.longitude}°E'
                ))

        if stations_updated > 0:
            self.stdout.write(f'\n已更新 {stations_updated} 個測站的座標\n')

        # 設定時間範圍
        start_date = datetime(2025, 12, 14, 0, 0, 0, tzinfo=taipei_tz)
        end_date = datetime(2025, 12, 21, 23, 59, 59, tzinfo=taipei_tz)
        interval = timedelta(minutes=10)

        self.stdout.write(f'\n開始生成數據:')
        self.stdout.write(f'  時間範圍: {start_date.strftime("%Y-%m-%d %H:%M")} ~ {end_date.strftime("%Y-%m-%d %H:%M")}')
        self.stdout.write(f'  間隔: {interval.total_seconds() / 60} 分鐘')
        self.stdout.write(f'  測站數: {stations.count()}')

        total_readings = 0

        for station in stations:
            self.stdout.write(f'\n處理測站: {station.station_name}')

            if not station.latitude or not station.longitude:
                self.stdout.write(self.style.WARNING(f'  ⚠ 跳過 (未設定經緯度)'))
                continue

            # 判斷測站屬於哪個海域（根據座標）
            station_lat = float(station.latitude)
            station_lng = float(station.longitude)

            # 找出最接近的海域
            current_area = None
            for area_key, area_data in SEA_AREAS.items():
                lat_min, lat_max = area_data['lat_range']
                lng_min, lng_max = area_data['lng_range']
                if lat_min <= station_lat <= lat_max and lng_min <= station_lng <= lng_max:
                    current_area = area_data
                    self.stdout.write(f'  海域: {area_data["name"]}')
                    break

            # 如果找不到匹配的海域，使用預設範圍（潮境）
            if not current_area:
                current_area = SEA_AREAS['chaojing']
                self.stdout.write(f'  使用預設海域: {current_area["name"]}')

            LAT_MIN, LAT_MAX = current_area['lat_range']
            LNG_MIN, LNG_MAX = current_area['lng_range']

            station_readings = 0
            current_time = start_date

            # 初始化 GPS 位置（從測站基礎位置開始）
            current_lat = station_lat
            current_lng = station_lng

            # 模擬主要洋流方向（東北向，帶有隨機擾動）
            # 這會產生更連貫的漂移軌跡
            drift_direction_lat = random.uniform(0.00005, 0.00015)  # 主要向北漂移
            drift_direction_lng = random.uniform(0.00005, 0.00015)  # 主要向東漂移

            while current_time <= end_date:
                # 生成連貫的 GPS 漂移（模擬洋流帶動儀器緩慢移動）
                # 主要漂移方向 + 隨機擾動
                lat_drift = drift_direction_lat + random.uniform(-0.00005, 0.00005)
                lng_drift = drift_direction_lng + random.uniform(-0.00005, 0.00005)

                current_lat += lat_drift
                current_lng += lng_drift

                # 確保保持在該測站對應的海域範圍內
                # 如果超出範圍，反彈回來（模擬儀器遇到邊界後改變方向）
                if current_lat < LAT_MIN:
                    current_lat = LAT_MIN + 0.001
                    drift_direction_lat = abs(drift_direction_lat)  # 改為向北
                elif current_lat > LAT_MAX:
                    current_lat = LAT_MAX - 0.001
                    drift_direction_lat = -abs(drift_direction_lat)  # 改為向南

                if current_lng < LNG_MIN:
                    current_lng = LNG_MIN + 0.001
                    drift_direction_lng = abs(drift_direction_lng)  # 改為向東
                elif current_lng > LNG_MAX:
                    current_lng = LNG_MAX - 0.001
                    drift_direction_lng = -abs(drift_direction_lng)  # 改為向西

                # 偶爾改變漂移方向（模擬洋流變化）
                if random.random() < 0.05:  # 5% 機率改變方向
                    drift_direction_lat += random.uniform(-0.0001, 0.0001)
                    drift_direction_lng += random.uniform(-0.0001, 0.0001)

                # 生成環境數據（帶日週期變化）
                hour = current_time.hour
                import math
                diurnal = (math.sin((hour - 6) * math.pi / 12) + 1) / 2

                # 基礎參數
                temperature = 25.0 + diurnal * 3.0 + random.uniform(-0.5, 0.5)
                salinity = 33.5 + random.uniform(-0.3, 0.3)
                oxygen = 8.0 + (1 - diurnal) * 1.5 + random.uniform(-0.3, 0.3)
                ph = 8.2 + random.uniform(-0.2, 0.2)
                conductivity = 54000.0 + random.uniform(-300, 300)
                pressure = 0.6 + random.uniform(-0.03, 0.03)
                fluorescence = 0.5 + diurnal * 0.8 + random.uniform(-0.1, 0.1)
                turbidity = random.uniform(3.0, 7.0)

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
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS(f'[完成] 總共生成 {total_readings} 筆數據'))
        self.stdout.write(f'  平均每測站: {total_readings // stations.count() if stations.count() > 0 else 0} 筆')

        # 計算預期數量
        expected_per_station = int((end_date - start_date).total_seconds() / interval.total_seconds()) + 1
        self.stdout.write(f'  預期每測站: {expected_per_station} 筆')
