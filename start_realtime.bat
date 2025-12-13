@echo off
REM 海洋監測系統 - 實時模擬功能啟動腳本 (Windows)
REM 使用方法: start_realtime.bat

setlocal enabledelayedexpansion

echo.
echo 🌊 海洋監測系統 - 實時模擬系統啟動
echo ====================================

REM 檢查虛擬環境
if not exist "venv" (
    echo.
    echo 正在建立虛擬環境...
    python -m venv venv
    echo ✓ 虛擬環境已建立
)

REM 激活虛擬環境
call venv\Scripts\activate.bat

REM 檢查依賴
echo.
echo 檢查依賴...
pip install -q -r requirements.txt > nul 2>&1
echo ✓ 依賴已檢查

REM 運行遷移
echo.
echo 正在初始化數據庫...
python manage.py migrate --noinput > nul 2>&1
echo ✓ 數據庫已初始化

REM 檢查/建立測站
echo.
echo 檢查測站數據...
python << PYSCRIPT
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from data_ingestion.models import Station
from datetime import datetime

if not Station.objects.exists():
    Station.objects.get_or_create(
        station_name='ChaoJingCR1000X',
        defaults={
            'device_model': 'CR1000X',
            'location': '潮境漁港',
            'install_date': datetime(2024, 8, 1).date()
        }
    )
    print("✓ 測站已建立")
else:
    print("✓ 測站已存在")
PYSCRIPT

echo.
echo 環境準備完成！
echo.
echo 📖 使用說明
echo ====================================
echo.
echo 現在將為你啟動 3 個服務:
echo.
echo 1️⃣  Django 開發伺服器
echo    訪問: http://localhost:8000/station_data/
echo.
echo 2️⃣  Celery Worker (背景任務處理)
echo    處理定時任務
echo.
echo 3️⃣  Celery Beat (定時排程)
echo    每 2 分鐘自動生成一次數據
echo.
echo 🌐 查看實時數據:
echo    http://localhost:8000/station_data/stations/1/
echo.
echo 📊 監控任務執行 (可選):
echo    celery -A config flower
echo    訪問: http://localhost:5555
echo.
echo 🔧 手動生成數據 (測試):
echo    python manage.py simulate_ocean_data
echo    python manage.py simulate_ocean_data --count=10
echo.
echo 📚 詳細文檔:
echo    - QUICKSTART.md      (快速開始)
echo    - REALTIME_GUIDE.md  (完整指南)
echo.
echo 按任意鍵繼續...
pause > nul

REM 建立日誌目錄
if not exist "logs" mkdir logs

echo.
echo 🚀 啟動服務...
echo.
echo 1️⃣  啟動 Django 開發伺服器
start "Django" cmd /k python manage.py runserver 0.0.0.0:8000

REM 等待 Django 啟動
timeout /t 3 > nul

echo 2️⃣  啟動 Celery Worker
start "Celery Worker" cmd /k celery -A config worker -l info

REM 等待 Worker 啟動
timeout /t 2 > nul

echo 3️⃣  啟動 Celery Beat
start "Celery Beat" cmd /k celery -A config beat -l info

echo.
echo ✓ 所有服務已啟動！
echo.
echo 四個新窗口已開啟:
echo   - Django (localhost:8000)
echo   - Celery Worker
echo   - Celery Beat
echo   - 此控制台
echo.
echo ⏹️  關閉相應窗口即可停止服務
echo.

pause
