"""
修復 Zeabur 資料庫缺少 latitude 和 longitude 欄位的問題
使用方法: python manage.py fix_db_columns
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = '修復 data_ingestion_station 表缺少的 latitude 和 longitude 欄位'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            self.stdout.write('檢查並修復資料庫欄位...')

            # 檢查 latitude 欄位
            cursor.execute("""
                SELECT COUNT(*)
                FROM information_schema.columns
                WHERE table_name = 'data_ingestion_station'
                AND column_name = 'latitude'
            """)
            latitude_exists = cursor.fetchone()[0] > 0

            # 檢查 longitude 欄位
            cursor.execute("""
                SELECT COUNT(*)
                FROM information_schema.columns
                WHERE table_name = 'data_ingestion_station'
                AND column_name = 'longitude'
            """)
            longitude_exists = cursor.fetchone()[0] > 0

            # 新增 latitude 欄位
            if not latitude_exists:
                self.stdout.write('新增 latitude 欄位...')
                cursor.execute("""
                    ALTER TABLE data_ingestion_station
                    ADD COLUMN latitude NUMERIC(9, 6) NULL
                """)
                self.stdout.write(self.style.SUCCESS('✓ latitude 欄位已新增'))
            else:
                self.stdout.write(self.style.WARNING('○ latitude 欄位已存在'))

            # 新增 longitude 欄位
            if not longitude_exists:
                self.stdout.write('新增 longitude 欄位...')
                cursor.execute("""
                    ALTER TABLE data_ingestion_station
                    ADD COLUMN longitude NUMERIC(9, 6) NULL
                """)
                self.stdout.write(self.style.SUCCESS('✓ longitude 欄位已新增'))
            else:
                self.stdout.write(self.style.WARNING('○ longitude 欄位已存在'))

            # 驗證結果
            self.stdout.write('\n驗證欄位狀態:')
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
                    f'  • {column_name}: {data_type} (nullable: {is_nullable})'
                )

            self.stdout.write(self.style.SUCCESS('\n✓ 資料庫修復完成!'))
