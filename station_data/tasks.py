"""
Celery 任務定義

這裡定義所有 station_data app 的背景任務
"""
from celery import shared_task
from datetime import datetime


@shared_task
def update_ocean_data_from_source():
    """
    定時從資料來源更新海洋數據

    這個任務會由 Celery Beat 定時執行（預設每分鐘一次）
    使用 OceanDataSimulator 生成真實的海洋數據模擬
    """
    from .simulation import simulate_data_for_all_stations

    print("[定時任務] 開始更新海洋數據...")

    result = simulate_data_for_all_stations()

    if result['status'] == 'success':
        print(f"[定時任務] 成功生成 {result['count']} 筆數據記錄")
        for reading in result['readings']:
            print(f"  - {reading['station_name']}: {reading['temperature']}°C, "
                  f"pH={reading['ph']}, 溶氧={reading['oxygen']}mg/L, "
                  f"鹽度={reading['salinity']}psu")
    else:
        print(f"[定時任務] 錯誤: {result['message']}")

    return result


@shared_task
def check_ocean_data_alerts():
    """
    檢查海洋數據異常並發送警告（定時任務）

    這個任務會由 Celery Beat 定時執行
    檢查項目：
    - 溫度異常（過高或過低）
    - pH 值異常
    - 溶氧量過低
    """
    from data_ingestion.models import Reading
    from django.utils import timezone
    from datetime import timedelta

    print("[定時任務] 開始檢查海洋數據異常...")

    # 取得最近 24 小時的數據
    yesterday = timezone.now() - timedelta(hours=24)
    recent_readings = Reading.objects.filter(timestamp__gte=yesterday)

    alerts = []

    # 檢查溫度異常（超過 30°C 或低於 15°C）
    high_temp = recent_readings.filter(temperature__gt=30).count()
    low_temp = recent_readings.filter(temperature__lt=15).count()

    if high_temp > 0:
        alerts.append(f'發現 {high_temp} 筆高溫數據（>30°C）')
    if low_temp > 0:
        alerts.append(f'發現 {low_temp} 筆低溫數據（<15°C）')

    # 檢查 pH 值異常（正常範圍 7.5-8.5）
    abnormal_ph = recent_readings.filter(ph__isnull=False).exclude(
        ph__gte=7.5, ph__lte=8.5
    ).count()

    if abnormal_ph > 0:
        alerts.append(f'發現 {abnormal_ph} 筆 pH 值異常（不在 7.5-8.5 範圍）')

    # 檢查溶氧量過低（< 6 mg/L）
    low_oxygen = recent_readings.filter(oxygen__lt=6, oxygen__isnull=False).count()

    if low_oxygen > 0:
        alerts.append(f'發現 {low_oxygen} 筆溶氧量過低（<6 mg/L）')

    if alerts:
        print(f"[定時任務] 發現 {len(alerts)} 個警告")
        for alert in alerts:
            print(f"  - {alert}")
    else:
        print("[定時任務] 所有數據正常")

    return {
        'status': 'success',
        'alerts_count': len(alerts),
        'alerts': alerts,
    }


@shared_task
def generate_daily_statistics():
    """
    產生每日統計報告（定時任務）

    這個任務會：
    1. 生成全系統統計報告（所有測站）
    2. 為每個測站生成獨立的統計報告

    統計項目：
    - 各測站數據筆數
    - 平均溫度、鹽度、溶氧等 8 個參數
    - 異常數據數量
    """
    from data_ingestion.models import Station, Reading
    from station_data.models import Report
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Avg, Count, Max, Min

    print("[定時任務] 開始產生每日統計報告...")

    # 取得今天的數據
    today = timezone.now().date()
    today_start = timezone.make_aware(datetime.combine(today, datetime.min.time()))
    today_readings = Reading.objects.filter(timestamp__gte=today_start)

    # 統計各測站數據筆數
    station_stats = []
    for station in Station.objects.all():
        count = today_readings.filter(station=station).count()
        station_stats.append({
            'station_name': station.station_name,
            'today_count': count,
            'location': station.location
        })

    # 計算平均值和範圍 (8個完整參數,每個都有 min/max)
    avg_stats = today_readings.aggregate(
        # 溫度
        avg_temperature=Avg('temperature'),
        max_temperature=Max('temperature'),
        min_temperature=Min('temperature'),
        # pH
        avg_ph=Avg('ph'),
        max_ph=Max('ph'),
        min_ph=Min('ph'),
        # 溶氧
        avg_oxygen=Avg('oxygen'),
        max_oxygen=Max('oxygen'),
        min_oxygen=Min('oxygen'),
        # 鹽度
        avg_salinity=Avg('salinity'),
        max_salinity=Max('salinity'),
        min_salinity=Min('salinity'),
        # 電導率
        avg_conductivity=Avg('conductivity'),
        max_conductivity=Max('conductivity'),
        min_conductivity=Min('conductivity'),
        # 壓力
        avg_pressure=Avg('pressure'),
        max_pressure=Max('pressure'),
        min_pressure=Min('pressure'),
        # 螢光值
        avg_fluorescence=Avg('fluorescence'),
        max_fluorescence=Max('fluorescence'),
        min_fluorescence=Min('fluorescence'),
        # 濁度
        avg_turbidity=Avg('turbidity'),
        max_turbidity=Max('turbidity'),
        min_turbidity=Min('turbidity'),
    )

    total_readings = today_readings.count()

    print(f"[定時任務] 今日數據筆數: {total_readings}")
    print(f"[定時任務] 平均溫度: {avg_stats['avg_temperature']:.2f}°C" if avg_stats['avg_temperature'] else "[定時任務] 無溫度數據")

    # 生成報告摘要
    summary_lines = [
        f"總數據筆數: {total_readings}",
        f"監測測站數: {len(station_stats)}",
    ]
    if avg_stats['avg_temperature']:
        summary_lines.append(f"平均溫度: {float(avg_stats['avg_temperature']):.2f}°C")
    if avg_stats['avg_salinity']:
        summary_lines.append(f"平均鹽度: {float(avg_stats['avg_salinity']):.4f}")

    # 保存報告到數據庫 (包含完整的 8 個參數及其 min/max)
    report = Report.objects.create(
        report_type='daily_statistics',
        title=f'{today} 每日統計報告',
        status='success' if total_readings > 0 else 'warning',
        summary='\n'.join(summary_lines),
        content={
            'date': today.isoformat(),
            'total_readings': total_readings,
            'station_stats': station_stats,
            'averages': {
                # 平均值
                'temperature': float(avg_stats['avg_temperature']) if avg_stats['avg_temperature'] else None,
                'ph': float(avg_stats['avg_ph']) if avg_stats['avg_ph'] else None,
                'oxygen': float(avg_stats['avg_oxygen']) if avg_stats['avg_oxygen'] else None,
                'salinity': float(avg_stats['avg_salinity']) if avg_stats['avg_salinity'] else None,
                'conductivity': float(avg_stats['avg_conductivity']) if avg_stats['avg_conductivity'] else None,
                'pressure': float(avg_stats['avg_pressure']) if avg_stats['avg_pressure'] else None,
                'fluorescence': float(avg_stats['avg_fluorescence']) if avg_stats['avg_fluorescence'] else None,
                'turbidity': float(avg_stats['avg_turbidity']) if avg_stats['avg_turbidity'] else None,
                # 最大值
                'max_temperature': float(avg_stats['max_temperature']) if avg_stats['max_temperature'] else None,
                'max_ph': float(avg_stats['max_ph']) if avg_stats['max_ph'] else None,
                'max_oxygen': float(avg_stats['max_oxygen']) if avg_stats['max_oxygen'] else None,
                'max_salinity': float(avg_stats['max_salinity']) if avg_stats['max_salinity'] else None,
                'max_conductivity': float(avg_stats['max_conductivity']) if avg_stats['max_conductivity'] else None,
                'max_pressure': float(avg_stats['max_pressure']) if avg_stats['max_pressure'] else None,
                'max_fluorescence': float(avg_stats['max_fluorescence']) if avg_stats['max_fluorescence'] else None,
                'max_turbidity': float(avg_stats['max_turbidity']) if avg_stats['max_turbidity'] else None,
                # 最小值
                'min_temperature': float(avg_stats['min_temperature']) if avg_stats['min_temperature'] else None,
                'min_ph': float(avg_stats['min_ph']) if avg_stats['min_ph'] else None,
                'min_oxygen': float(avg_stats['min_oxygen']) if avg_stats['min_oxygen'] else None,
                'min_salinity': float(avg_stats['min_salinity']) if avg_stats['min_salinity'] else None,
                'min_conductivity': float(avg_stats['min_conductivity']) if avg_stats['min_conductivity'] else None,
                'min_pressure': float(avg_stats['min_pressure']) if avg_stats['min_pressure'] else None,
                'min_fluorescence': float(avg_stats['min_fluorescence']) if avg_stats['min_fluorescence'] else None,
                'min_turbidity': float(avg_stats['min_turbidity']) if avg_stats['min_turbidity'] else None,
            }
        },
    )

    print(f"[定時任務] 全系統報告已保存，ID: {report.id}")

    # ==========================================
    # 為每個測站生成獨立的統計報告
    # ==========================================
    station_report_ids = []

    for station in Station.objects.all():
        # 取得該測站今天的數據
        station_today_readings = today_readings.filter(station=station)
        station_count = station_today_readings.count()

        if station_count == 0:
            print(f"[定時任務] 測站 {station.station_name} 今日無數據，跳過")
            continue

        # 計算該測站的平均值和範圍
        station_stats_agg = station_today_readings.aggregate(
            # 溫度
            avg_temperature=Avg('temperature'),
            max_temperature=Max('temperature'),
            min_temperature=Min('temperature'),
            # pH
            avg_ph=Avg('ph'),
            max_ph=Max('ph'),
            min_ph=Min('ph'),
            # 溶氧
            avg_oxygen=Avg('oxygen'),
            max_oxygen=Max('oxygen'),
            min_oxygen=Min('oxygen'),
            # 鹽度
            avg_salinity=Avg('salinity'),
            max_salinity=Max('salinity'),
            min_salinity=Min('salinity'),
            # 電導率
            avg_conductivity=Avg('conductivity'),
            max_conductivity=Max('conductivity'),
            min_conductivity=Min('conductivity'),
            # 壓力
            avg_pressure=Avg('pressure'),
            max_pressure=Max('pressure'),
            min_pressure=Min('pressure'),
            # 螢光值
            avg_fluorescence=Avg('fluorescence'),
            max_fluorescence=Max('fluorescence'),
            min_fluorescence=Min('fluorescence'),
            # 濁度
            avg_turbidity=Avg('turbidity'),
            max_turbidity=Max('turbidity'),
            min_turbidity=Min('turbidity'),
        )

        # 生成測站報告摘要
        station_summary_lines = [
            f"測站: {station.station_name} ({station.location})",
            f"數據筆數: {station_count}",
        ]
        if station_stats_agg['avg_temperature']:
            station_summary_lines.append(f"平均溫度: {float(station_stats_agg['avg_temperature']):.2f}°C")
        if station_stats_agg['avg_salinity']:
            station_summary_lines.append(f"平均鹽度: {float(station_stats_agg['avg_salinity']):.4f}")

        # 保存測站報告
        station_report = Report.objects.create(
            report_type='station_daily',
            station=station,  # 關聯到特定測站
            title=f'{today} {station.station_name} 每日統計',
            status='success' if station_count > 0 else 'warning',
            summary='\n'.join(station_summary_lines),
            content={
                'date': today.isoformat(),
                'station_id': station.id,
                'station_name': station.station_name,
                'station_location': station.location,
                'total_readings': station_count,
                'averages': {
                    # 平均值
                    'temperature': float(station_stats_agg['avg_temperature']) if station_stats_agg['avg_temperature'] else None,
                    'ph': float(station_stats_agg['avg_ph']) if station_stats_agg['avg_ph'] else None,
                    'oxygen': float(station_stats_agg['avg_oxygen']) if station_stats_agg['avg_oxygen'] else None,
                    'salinity': float(station_stats_agg['avg_salinity']) if station_stats_agg['avg_salinity'] else None,
                    'conductivity': float(station_stats_agg['avg_conductivity']) if station_stats_agg['avg_conductivity'] else None,
                    'pressure': float(station_stats_agg['avg_pressure']) if station_stats_agg['avg_pressure'] else None,
                    'fluorescence': float(station_stats_agg['avg_fluorescence']) if station_stats_agg['avg_fluorescence'] else None,
                    'turbidity': float(station_stats_agg['avg_turbidity']) if station_stats_agg['avg_turbidity'] else None,
                    # 最大值
                    'max_temperature': float(station_stats_agg['max_temperature']) if station_stats_agg['max_temperature'] else None,
                    'max_ph': float(station_stats_agg['max_ph']) if station_stats_agg['max_ph'] else None,
                    'max_oxygen': float(station_stats_agg['max_oxygen']) if station_stats_agg['max_oxygen'] else None,
                    'max_salinity': float(station_stats_agg['max_salinity']) if station_stats_agg['max_salinity'] else None,
                    'max_conductivity': float(station_stats_agg['max_conductivity']) if station_stats_agg['max_conductivity'] else None,
                    'max_pressure': float(station_stats_agg['max_pressure']) if station_stats_agg['max_pressure'] else None,
                    'max_fluorescence': float(station_stats_agg['max_fluorescence']) if station_stats_agg['max_fluorescence'] else None,
                    'max_turbidity': float(station_stats_agg['max_turbidity']) if station_stats_agg['max_turbidity'] else None,
                    # 最小值
                    'min_temperature': float(station_stats_agg['min_temperature']) if station_stats_agg['min_temperature'] else None,
                    'min_ph': float(station_stats_agg['min_ph']) if station_stats_agg['min_ph'] else None,
                    'min_oxygen': float(station_stats_agg['min_oxygen']) if station_stats_agg['min_oxygen'] else None,
                    'min_salinity': float(station_stats_agg['min_salinity']) if station_stats_agg['min_salinity'] else None,
                    'min_conductivity': float(station_stats_agg['min_conductivity']) if station_stats_agg['min_conductivity'] else None,
                    'min_pressure': float(station_stats_agg['min_pressure']) if station_stats_agg['min_pressure'] else None,
                    'min_fluorescence': float(station_stats_agg['min_fluorescence']) if station_stats_agg['min_fluorescence'] else None,
                    'min_turbidity': float(station_stats_agg['min_turbidity']) if station_stats_agg['min_turbidity'] else None,
                }
            },
        )

        station_report_ids.append(station_report.id)
        print(f"[定時任務] 測站 {station.station_name} 報告已保存，ID: {station_report.id}")

    print(f"[定時任務] 完成！生成了 1 個全系統報告 + {len(station_report_ids)} 個測站報告")

    return {
        'status': 'success',
        'system_report_id': report.id,
        'station_report_ids': station_report_ids,
        'station_report_count': len(station_report_ids),
        'date': today.isoformat(),
        'total_readings': total_readings,
        'station_stats': station_stats,
        'averages': avg_stats,
    }


# ==========================================
# Google Sheets 整合範例（需安裝 gspread）
# ==========================================

def fetch_from_google_sheets():
    """
    從 Google Sheets 讀取數據

    需要安裝: pip install gspread oauth2client
    需要設定: Google Service Account credentials

    使用方式：
    1. 前往 Google Cloud Console 建立 Service Account
    2. 下載 credentials.json
    3. 在 Google Sheets 中分享給 service account email
    """
    # import gspread
    # from oauth2client.service_account import ServiceAccountCredentials
    #
    # scope = ['https://spreadsheets.google.com/feeds',
    #          'https://www.googleapis.com/auth/drive']
    #
    # creds = ServiceAccountCredentials.from_json_keyfile_name(
    #     'path/to/credentials.json', scope)
    # client = gspread.authorize(creds)
    #
    # # 開啟 Google Sheet
    # sheet = client.open('海洋監測數據').sheet1
    #
    # # 讀取所有資料
    # data = sheet.get_all_records()
    #
    # return data

    pass


def fetch_from_database():
    """
    從外部資料庫讀取數據

    需要安裝對應的資料庫驅動：
    - PostgreSQL: psycopg2
    - MySQL: mysqlclient
    - SQL Server: pyodbc
    """
    # import psycopg2
    #
    # conn = psycopg2.connect(
    #     host="your_host",
    #     database="your_db",
    #     user="your_user",
    #     password="your_password"
    # )
    #
    # cursor = conn.cursor()
    # cursor.execute("SELECT * FROM ocean_data WHERE timestamp > NOW() - INTERVAL '1 hour'")
    # data = cursor.fetchall()
    #
    # conn.close()
    # return data

    pass


def fetch_from_external_api():
    """
    從外部 API 讀取數據

    需要安裝: pip install requests
    """
    # import requests
    #
    # response = requests.get('https://api.example.com/ocean-data')
    # data = response.json()
    #
    # return data

    pass


# ==========================================
# 使用者通知任務（用於動態排程）
# ==========================================

@shared_task
def send_data_alert_notification(user_id=None):
    """
    發送數據異常通知（可針對特定使用者）

    這個任務可以透過 django-celery-beat 動態排程

    Args:
        user_id: 可選的使用者 ID，如果提供則只通知該使用者
    """
    from data_ingestion.models import Reading
    from apps.core.accounts.models import User
    from django.utils import timezone
    from datetime import timedelta

    print(f"[通知任務] 開始檢查數據異常...")
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            print(f"[通知任務] 為使用者 {user.username} 檢查")
        except User.DoesNotExist:
            print(f"[通知任務] 使用者 {user_id} 不存在")
            return {'status': 'error', 'message': 'User not found'}

    # 取得最近 1 小時的數據
    one_hour_ago = timezone.now() - timedelta(hours=1)
    recent_readings = Reading.objects.filter(timestamp__gte=one_hour_ago)

    alerts = []

    # 檢查溫度異常
    high_temp = recent_readings.filter(temperature__gt=30).count()
    if high_temp > 0:
        alerts.append(f'發現 {high_temp} 筆高溫數據（>30°C）')

    # 檢查 pH 值異常
    abnormal_ph = recent_readings.filter(ph__isnull=False).exclude(
        ph__gte=7.5, ph__lte=8.5
    ).count()
    if abnormal_ph > 0:
        alerts.append(f'發現 {abnormal_ph} 筆 pH 值異常')

    # 檢查溶氧量過低
    low_oxygen = recent_readings.filter(oxygen__lt=6, oxygen__isnull=False).count()
    if low_oxygen > 0:
        alerts.append(f'發現 {low_oxygen} 筆溶氧量過低')

    if alerts:
        print(f"[通知任務] 發現 {len(alerts)} 個警告")
        for alert in alerts:
            print(f"  - {alert}")
        # TODO: 這裡可以加入發送 Email、推播等通知機制
    else:
        print("[通知任務] 所有數據正常")

    return {
        'status': 'success',
        'user_id': user_id,
        'alerts_count': len(alerts),
        'alerts': alerts,
    }
