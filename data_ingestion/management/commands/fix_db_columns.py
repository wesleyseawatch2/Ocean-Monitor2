"""
修復 Zeabur 資料庫缺少 latitude 和 longitude 欄位的問題
使用方法: python manage.py fix_db_columns
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = '修復 Station 和 Reading 表缺少的 latitude 和 longitude 欄位'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            self.stdout.write('檢查並修復資料庫欄位...\n')

            # ==========================================
            # 修復 Station 表
            # ==========================================
            self.stdout.write(self.style.MIGRATE_HEADING('📍 檢查 Station 表'))

            # 檢查 Station latitude 欄位
            cursor.execute("""
                SELECT COUNT(*)
                FROM information_schema.columns
                WHERE table_name = 'data_ingestion_station'
                AND column_name = 'latitude'
            """)
            station_lat_exists = cursor.fetchone()[0] > 0

            # 檢查 Station longitude 欄位
            cursor.execute("""
                SELECT COUNT(*)
                FROM information_schema.columns
                WHERE table_name = 'data_ingestion_station'
                AND column_name = 'longitude'
            """)
            station_lng_exists = cursor.fetchone()[0] > 0

            # 新增 Station latitude 欄位
            if not station_lat_exists:
                self.stdout.write('  新增 Station.latitude 欄位...')
                cursor.execute("""
                    ALTER TABLE data_ingestion_station
                    ADD COLUMN latitude NUMERIC(9, 6) NULL
                """)
                self.stdout.write(self.style.SUCCESS('  ✓ Station.latitude 欄位已新增'))
            else:
                self.stdout.write(self.style.WARNING('  ○ Station.latitude 欄位已存在'))

            # 新增 Station longitude 欄位
            if not station_lng_exists:
                self.stdout.write('  新增 Station.longitude 欄位...')
                cursor.execute("""
                    ALTER TABLE data_ingestion_station
                    ADD COLUMN longitude NUMERIC(9, 6) NULL
                """)
                self.stdout.write(self.style.SUCCESS('  ✓ Station.longitude 欄位已新增'))
            else:
                self.stdout.write(self.style.WARNING('  ○ Station.longitude 欄位已存在'))

            # ==========================================
            # 修復 Reading 表
            # ==========================================
            self.stdout.write('\n' + self.style.MIGRATE_HEADING('📊 檢查 Reading 表'))

            # 檢查 Reading latitude 欄位
            cursor.execute("""
                SELECT COUNT(*)
                FROM information_schema.columns
                WHERE table_name = 'data_ingestion_reading'
                AND column_name = 'latitude'
            """)
            reading_lat_exists = cursor.fetchone()[0] > 0

            # 檢查 Reading longitude 欄位
            cursor.execute("""
                SELECT COUNT(*)
                FROM information_schema.columns
                WHERE table_name = 'data_ingestion_reading'
                AND column_name = 'longitude'
            """)
            reading_lng_exists = cursor.fetchone()[0] > 0

            # 新增 Reading latitude 欄位
            if not reading_lat_exists:
                self.stdout.write('  新增 Reading.latitude 欄位...')
                cursor.execute("""
                    ALTER TABLE data_ingestion_reading
                    ADD COLUMN latitude NUMERIC(9, 6) NULL
                """)
                self.stdout.write(self.style.SUCCESS('  ✓ Reading.latitude 欄位已新增'))
            else:
                self.stdout.write(self.style.WARNING('  ○ Reading.latitude 欄位已存在'))

            # 新增 Reading longitude 欄位
            if not reading_lng_exists:
                self.stdout.write('  新增 Reading.longitude 欄位...')
                cursor.execute("""
                    ALTER TABLE data_ingestion_reading
                    ADD COLUMN longitude NUMERIC(9, 6) NULL
                """)
                self.stdout.write(self.style.SUCCESS('  ✓ Reading.longitude 欄位已新增'))
            else:
                self.stdout.write(self.style.WARNING('  ○ Reading.longitude 欄位已存在'))

            # ==========================================
            # 驗證結果
            # ==========================================
            self.stdout.write('\n' + self.style.MIGRATE_HEADING('✅ 驗證欄位狀態'))

            # Station 表驗證
            self.stdout.write('  Station 表:')
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'data_ingestion_station'
                AND column_name IN ('latitude', 'longitude')
                ORDER BY column_name
            """)
            for row in cursor.fetchall():
                column_name, data_type, is_nullable = row
                self.stdout.write(
                    f'    • {column_name}: {data_type} (nullable: {is_nullable})'
                )

            # Reading 表驗證
            self.stdout.write('  Reading 表:')
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'data_ingestion_reading'
                AND column_name IN ('latitude', 'longitude')
                ORDER BY column_name
            """)
            for row in cursor.fetchall():
                column_name, data_type, is_nullable = row
                self.stdout.write(
                    f'    • {column_name}: {data_type} (nullable: {is_nullable})'
                )

            self.stdout.write('\n' + self.style.SUCCESS('✓ 資料庫修復完成!'))
