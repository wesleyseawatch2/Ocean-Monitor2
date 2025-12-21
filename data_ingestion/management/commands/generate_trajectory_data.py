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

        # 自動為沒有經緯度的測站設置海上初始座標（潮境公園外海）
        # 潮境公園座標: 121.7813°E, 25.1365°N
        # 外海區域: 往東北方向偏移到海上
        stations_updated = 0
        for station in stations:
            if not station.latitude or not station.longitude:
                # 潮境公園東北外海區域（約 2-3 公里外的海上）
                station.latitude = Decimal('25.1550')  # 往北偏移約 2 公里
                station.longitude = Decimal('121.8050')  # 往東偏移約 2 公里
                station.save()
                stations_updated += 1
                self.stdout.write(self.style.SUCCESS(f'已為測站 "{station.station_name}" 設置潮境公園外海座標'))

        if stations_updated > 0:
            self.stdout.write(f'\n已更新 {stations_updated} 個測站的座標為潮境公園外海位置\n')

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

            station_readings = 0
            current_time = start_date

            # 初始化 GPS 位置（從測站基礎位置開始）
            current_lat = float(station.latitude)
            current_lng = float(station.longitude)

            while current_time <= end_date:
                # 生成 GPS 漂移（模擬海流和儀器緩慢漂移）
                # 每 10 分鐘移動約 10-30 米（0.0001-0.0003 度）
                lat_drift = random.uniform(-0.0003, 0.0003)  # 約 30 米
                lng_drift = random.uniform(-0.0003, 0.0003)  # 約 30 米
                current_lat += lat_drift
                current_lng += lng_drift

                # 限制漂移範圍不超過基礎位置 ±0.01 度（約 1.1 公里）
                # 確保儀器保持在海上區域，不會漂移太遠
                max_drift = 0.01
                current_lat = max(min(current_lat, float(station.latitude) + max_drift),
                                 float(station.latitude) - max_drift)
                current_lng = max(min(current_lng, float(station.longitude) + max_drift),
                                 float(station.longitude) - max_drift)

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
