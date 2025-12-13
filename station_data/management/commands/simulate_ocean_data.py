"""
管理命令：生成模擬海洋數據

使用方法:
    python manage.py simulate_ocean_data                    # 生成一次數據
    python manage.py simulate_ocean_data --continuous       # 持續生成（測試用）
    python manage.py simulate_ocean_data --count=10         # 生成 10 筆數據
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from station_data.simulation import simulate_data_for_all_stations
import time


class Command(BaseCommand):
    help = '生成模擬的海洋監測數據'

    def add_arguments(self, parser):
        parser.add_argument(
            '--continuous',
            action='store_true',
            help='持續生成數據（每分鐘一次，按 Ctrl+C 停止）',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=1,
            help='要生成的數據輪數（預設：1）',
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=60,
            help='連續模式下的生成間隔（秒，預設：60）',
        )

    def handle(self, *args, **options):
        continuous = options['continuous']
        count = options['count']
        interval = options['interval']

        if continuous:
            self.stdout.write(
                self.style.SUCCESS(
                    f'🌊 開始持續生成海洋數據（每 {interval} 秒一次，按 Ctrl+C 停止）\n'
                )
            )
            counter = 0
            try:
                while True:
                    counter += 1
                    self.stdout.write(f'\n[{counter}] ', ending='')
                    self.generate_data()
                    time.sleep(interval)
            except KeyboardInterrupt:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\n\n✓ 已停止。共生成 {counter} 輪數據。'
                    )
                )
        else:
            for i in range(count):
                self.stdout.write(f'[{i+1}/{count}] ', ending='')
                self.generate_data()
                if i < count - 1:
                    time.sleep(1)  # 各輪之間間隔 1 秒

            self.stdout.write(
                self.style.SUCCESS(f'\n✓ 已生成 {count} 輪數據。')
            )

    def generate_data(self):
        """生成一輪數據"""
        try:
            result = simulate_data_for_all_stations()

            if result['status'] == 'success':
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ 生成 {result['count']} 筆數據 @ {timezone.now().strftime('%H:%M:%S')}"
                    )
                )
                
                # 詳細信息
                for reading in result['readings']:
                    self.stdout.write(
                        f"  📍 {reading['station_name']}: "
                        f"溫度={reading['temperature']}°C, "
                        f"pH={reading['ph']}, "
                        f"溶氧={reading['oxygen']}mg/L, "
                        f"鹽度={reading['salinity']}psu"
                    )
            else:
                self.stdout.write(
                    self.style.ERROR(f"✗ 錯誤: {result['message']}")
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"✗ 生成失敗: {str(e)}")
            )
