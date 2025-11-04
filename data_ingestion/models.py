from django.db import models


class Station(models.Model):
    """測站資料表"""
    station_name = models.CharField(max_length=100, verbose_name="測站名稱")
    device_model = models.CharField(max_length=50, verbose_name="設備型號")
    location = models.CharField(max_length=100, verbose_name="裝設地點")
    install_date = models.DateField(verbose_name="裝設日期")
    
    class Meta:
        verbose_name = "測站"
        verbose_name_plural = "測站"
    
    def __str__(self):
        return f"{self.station_name} ({self.location})"


class Reading(models.Model):
    """數據記錄資料表"""
    station = models.ForeignKey(
        Station, 
        on_delete=models.CASCADE, 
        related_name='readings',
        verbose_name="測站"
    )
    timestamp = models.DateTimeField(verbose_name="時間戳")
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="溫度")
    conductivity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="電導率")
    pressure = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True, verbose_name="壓力")
    oxygen = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True, verbose_name="溶氧")
    ph = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="酸鹼值")
    fluorescence = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True, verbose_name="螢光值")
    turbidity = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True, verbose_name="濁度")
    salinity = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True, verbose_name="鹽度")
    
    class Meta:
        verbose_name = "數據記錄"
        verbose_name_plural = "數據記錄"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.station.station_name} - {self.timestamp}"