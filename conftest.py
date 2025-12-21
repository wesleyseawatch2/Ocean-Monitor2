"""
根目錄 conftest.py - 全專案共用的 Fixtures
"""
import pytest
from django.contrib.auth import get_user_model
from data_ingestion.models import Station, Reading
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone
from django.contrib.sites.models import Site

User = get_user_model()


# ==========================================
# Django Sites & Allauth 設定
# ==========================================

@pytest.fixture(autouse=True)
def setup_site_and_social_app(db):
    """自動設定 Django Site 和 Google Social App（測試環境需要）"""
    try:
        from allauth.socialaccount.models import SocialApp

        # 建立或取得 Site
        site, _ = Site.objects.get_or_create(
            id=1,
            defaults={'domain': 'testserver', 'name': 'Test Server'}
        )

        # 建立 Google Social App（如果不存在）
        google_app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google (Test)',
                'client_id': 'test-client-id',
                'secret': 'test-secret',
            }
        )

        # 關聯到 Site
        if site not in google_app.sites.all():
            google_app.sites.add(site)
    except:
        # 如果 allauth 未安裝，忽略
        pass


# ==========================================
# 使用者相關 Fixtures
# ==========================================

@pytest.fixture
def user(db):
    """建立一般測試使用者"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def staff_user(db):
    """建立管理員使用者"""
    return User.objects.create_user(
        username='adminuser',
        email='admin@example.com',
        password='adminpass123',
        is_staff=True
    )


@pytest.fixture
def authenticated_client(client, user):
    """已登入的一般使用者 client"""
    client.login(username='testuser', password='testpass123')
    return client


@pytest.fixture
def staff_authenticated_client(client, staff_user):
    """已登入的管理員 client"""
    client.login(username='adminuser', password='adminpass123')
    return client


# ==========================================
# 測站相關 Fixtures
# ==========================================

@pytest.fixture
def station(db):
    """建立測試用測站"""
    return Station.objects.create(
        station_name='測試測站A',
        device_model='Model-X100',
        location='台北港',
        install_date='2024-01-15',
        latitude=25.033964,
        longitude=121.564472
    )


@pytest.fixture
def station_b(db):
    """建立第二個測試用測站"""
    return Station.objects.create(
        station_name='測試測站B',
        device_model='Model-X200',
        location='基隆港',
        install_date='2024-02-20',
        latitude=25.128675,
        longitude=121.739435
    )


@pytest.fixture
def multiple_stations(db):
    """建立多個測試測站"""
    stations = []
    locations = [
        ('測站A', 'Model-A', '台北港', '2024-01-01', 25.033964, 121.564472),
        ('測站B', 'Model-B', '基隆港', '2024-01-02', 25.128675, 121.739435),
        ('測站C', 'Model-C', '高雄港', '2024-01-03', 22.619997, 120.266197),
    ]

    for name, model, location, date, lat, lng in locations:
        station = Station.objects.create(
            station_name=name,
            device_model=model,
            location=location,
            install_date=date,
            latitude=lat,
            longitude=lng
        )
        stations.append(station)

    return stations


# ==========================================
# 數據記錄相關 Fixtures
# ==========================================

@pytest.fixture
def reading(db, station):
    """建立單筆測試數據"""
    return Reading.objects.create(
        station=station,
        timestamp=timezone.now(),
        temperature=Decimal('25.5'),
        conductivity=Decimal('50000.00'),
        pressure=Decimal('10.123'),
        oxygen=Decimal('7.500'),
        ph=Decimal('8.20'),
        fluorescence=Decimal('1.234'),
        turbidity=Decimal('5.678'),
        salinity=Decimal('35.1234')
    )


@pytest.fixture
def multiple_readings(db, station):
    """建立多筆測試數據（時間序列）"""
    readings = []
    base_time = timezone.now() - timedelta(hours=10)

    for i in range(10):
        reading = Reading.objects.create(
            station=station,
            timestamp=base_time + timedelta(hours=i),
            temperature=Decimal(f'{20.0 + i}'),
            ph=Decimal(f'{7.0 + i * 0.1}'),
            oxygen=Decimal(f'{6.0 + i * 0.2}'),
            salinity=Decimal(f'{30.0 + i}')
        )
        readings.append(reading)

    return readings


@pytest.fixture
def readings_with_null_values(db, station):
    """建立包含 NULL 值的測試數據"""
    return [
        Reading.objects.create(
            station=station,
            timestamp=timezone.now(),
            temperature=Decimal('25.0'),
            ph=None,  # 故意設為 None
            oxygen=Decimal('7.0'),
            salinity=None  # 故意設為 None
        ),
        Reading.objects.create(
            station=station,
            timestamp=timezone.now() - timedelta(hours=1),
            temperature=None,
            ph=Decimal('8.0'),
            oxygen=None,
            salinity=Decimal('35.0')
        ),
    ]
