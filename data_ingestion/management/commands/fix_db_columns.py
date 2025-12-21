"""
修復 Zeabur 資料庫缺少 latitude 和 longitude 欄位的問題
使用方法: python manage.py fix_db_columns
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = '修復 Station 和 Reading 表缺少的 latitude 和 longitude 欄位'

    def check_column_exists(self, cursor, table_name, column_name):
        """檢查欄位是否存在"""
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.columns
            WHERE table_name = %s
            AND column_name = %s
        """, [table_name, column_name])
        return cursor.fetchone()[0] > 0

    def add_column_if_missing(self, cursor, table_name, column_name, display_name):
        """如果欄位不存在則新增"""
        if not self.check_column_exists(cursor, table_name, column_name):
            self.stdout.write(f'  新增 {display_name} 欄位...')
            try:
                cursor.execute(f"""
                    ALTER TABLE {table_name}
                    ADD COLUMN {column_name} NUMERIC(9, 6) NULL
                """)
                self.stdout.write(self.style.SUCCESS(f'  ✓ {display_name} 欄位已新增'))
                return True
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ 新增 {display_name} 失敗: {str(e)}'))
                return False
        else:
            self.stdout.write(self.style.WARNING(f'  ○ {display_name} 欄位已存在'))
            return False

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            self.stdout.write('檢查並修復資料庫欄位...\n')
            changes_made = False

            # ==========================================
            # 修復 Station 表
            # ==========================================
            self.stdout.write(self.style.MIGRATE_HEADING('📍 檢查 Station 表'))

            if self.add_column_if_missing(cursor, 'data_ingestion_station', 'latitude', 'Station.latitude'):
                changes_made = True
            if self.add_column_if_missing(cursor, 'data_ingestion_station', 'longitude', 'Station.longitude'):
                changes_made = True

            # ==========================================
            # 修復 Reading 表
            # ==========================================
            self.stdout.write('\n' + self.style.MIGRATE_HEADING('📊 檢查 Reading 表'))

            if self.add_column_if_missing(cursor, 'data_ingestion_reading', 'latitude', 'Reading.latitude'):
                changes_made = True
            if self.add_column_if_missing(cursor, 'data_ingestion_reading', 'longitude', 'Reading.longitude'):
                changes_made = True

            # ==========================================
            # 驗證結果
            # ==========================================
            if changes_made:
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

                self.stdout.write('\n' + self.style.SUCCESS('✓ 資料庫修復完成!已新增欄位'))
            else:
                self.stdout.write('\n' + self.style.SUCCESS('✓ 所有欄位都已存在,無需修復'))
