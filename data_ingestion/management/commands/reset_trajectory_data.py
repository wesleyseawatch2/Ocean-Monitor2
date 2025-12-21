"""
重置並重新生成軌跡數據
清除所有舊數據並生成新的12/14-12/21軌跡數據
使用方法: python manage.py reset_trajectory_data
"""
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = '重置並重新生成所有軌跡數據（危險操作！會刪除所有現有數據）'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('⚠️  警告：此操作將刪除所有現有的 Reading 數據！'))
        self.stdout.write(self.style.WARNING('⚠️  正在執行數據重置...'))

        # 呼叫 generate_trajectory_data 命令並傳遞 --clear 參數
        call_command('generate_trajectory_data', clear=True)

        self.stdout.write('\n' + self.style.SUCCESS('✓ 數據重置完成！'))
