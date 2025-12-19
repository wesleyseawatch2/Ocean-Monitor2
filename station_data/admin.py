# ocean_monitor\station_data\admin.py
from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'report_type', 'status', 'created_at']
    list_filter = ['report_type', 'status', 'created_at']
    search_fields = ['title', 'summary', 'task_id']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('基本資訊', {
            'fields': ('report_type', 'title', 'status')
        }),
        ('內容', {
            'fields': ('summary', 'content')
        }),
        ('系統資訊', {
            'fields': ('task_id', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        # 報告應由系統自動生成，不允許手動添加
        return False
