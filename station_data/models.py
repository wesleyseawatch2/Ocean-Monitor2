# ocean_monitor\station_data\models.py
from django.db import models
from django.utils import timezone


class Report(models.Model):
    """
    報告資料表 - 集中管理 Celery 任務產生的報告

    支援兩種報告類型：
    1. 全系統報告：不關聯特定測站，統計所有測站數據
    2. 測站報告：關聯特定測站，只統計該測站數據
    """

    REPORT_TYPES = [
        ('daily_statistics', '每日統計報告'),
        ('station_daily', '測站每日報告'),
        ('data_update', '數據更新報告'),
        ('alert_check', '異常檢查報告'),
        ('custom', '自定義報告'),
    ]

    STATUS_CHOICES = [
        ('success', '成功'),
        ('failed', '失敗'),
        ('warning', '警告'),
    ]

    report_type = models.CharField(
        max_length=50,
        choices=REPORT_TYPES,
        verbose_name="報告類型"
    )
    title = models.CharField(max_length=200, verbose_name="報告標題")

    # 測站關聯（可選）- 如果為 None 則表示全系統報告
    station = models.ForeignKey(
        'data_ingestion.Station',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='reports',
        verbose_name="關聯測站"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='success',
        verbose_name="狀態"
    )
    summary = models.TextField(verbose_name="摘要", blank=True)
    content = models.JSONField(verbose_name="報告內容", default=dict)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="創建時間")
    task_id = models.CharField(max_length=100, blank=True, verbose_name="Celery 任務 ID")

    class Meta:
        verbose_name = "報告"
        verbose_name_plural = "報告"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['report_type']),
        ]

    def __str__(self):
        return f"{self.get_report_type_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    def get_status_class(self):
        """返回狀態對應的 Bootstrap 類名"""
        status_map = {
            'success': 'success',
            'failed': 'danger',
            'warning': 'warning',
        }
        return status_map.get(self.status, 'secondary')
