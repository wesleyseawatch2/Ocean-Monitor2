import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from data_ingestion.models import Station, Reading

# 建立測站
station, created = Station.objects.get_or_create(
    station_name='ChaoJingCR1000X',
    defaults={
        'device_model': 'CR1000X',
        'location': '潮境漁港',
        'install_date': datetime(2024, 8, 1).date()
    }
)

# 建立範例數據
base_time = datetime(2024, 9, 3, 13, 0, 0)
for i in range(20):
    Reading.objects.create(
        station=station,
        timestamp=base_time + timedelta(minutes=i*10),
        temperature=29.37 + (i * 0.01),
        conductivity=54946.5 + (i * 50),
        pressure=0.59 + (i * 0.001),
        oxygen=7.89 + (i * 0.01),
        ph=8.09 + (i * 0.01),
        fluorescence=0.81 + (i * 0.02),
        turbidity=5.50 + (i * 0.1),
        salinity=33.12 + (i * 0.01)
    )

print(f"✓ 已建立測站：{station.station_name}")
print(f"✓ 已建立 {Reading.objects.count()} 筆數據記錄")