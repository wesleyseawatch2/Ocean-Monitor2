#!/bin/bash
# 海洋監測系統 - 實時模擬功能啟動腳本 (Linux/Mac)

echo "🌊 海洋監測系統 - 實時模擬系統啟動"
echo "===================================="

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 檢查必要的環境
check_requirements() {
    echo ""
    echo "📋 檢查環境..."
    
    # 檢查 Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}✗ Python 3 未安裝${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Python $(python3 --version)${NC}"
    
    # 檢查 Redis
    if ! command -v redis-cli &> /dev/null; then
        echo -e "${YELLOW}⚠ Redis 未找到（可選，但建議安裝）${NC}"
    else
        echo -e "${GREEN}✓ Redis 已安裝${NC}"
    fi
    
    # 檢查虛擬環境
    if [[ ! -d "venv" ]]; then
        echo -e "${YELLOW}⚠ 虛擬環境不存在，正在建立...${NC}"
        python3 -m venv venv
    fi
    
    # 激活虛擬環境
    source venv/bin/activate
    echo -e "${GREEN}✓ 虛擬環境已激活${NC}"
}

# 檢查數據庫
check_database() {
    echo ""
    echo "🗄️  檢查數據庫..."
    
    # 運行遷移
    python manage.py migrate --noinput > /dev/null 2>&1
    echo -e "${GREEN}✓ 數據庫遷移完成${NC}"
    
    # 檢查測站
    python manage.py shell << EOF
from data_ingestion.models import Station
from datetime import datetime

if not Station.objects.exists():
    print("🔧 建立測試測站...")
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
EOF
}

# 顯示使用說明
show_help() {
    echo ""
    echo "📖 使用說明"
    echo "===================================="
    echo ""
    echo "已為你啟動了 3 個終端窗口:"
    echo ""
    echo "1️⃣  Django 開發伺服器"
    echo "   訪問: http://localhost:8000/station_data/"
    echo ""
    echo "2️⃣  Celery Worker (背景任務處理)"
    echo "   處理定時任務"
    echo ""
    echo "3️⃣  Celery Beat (定時排程)"
    echo "   每 2 分鐘自動生成一次數據"
    echo ""
    echo "🌐 查看實時數據:"
    echo "   http://localhost:8000/station_data/stations/1/"
    echo ""
    echo "📊 監控任務執行 (可選):"
    echo "   在新終端運行: celery -A config flower"
    echo "   訪問: http://localhost:5555"
    echo ""
    echo "🔧 手動生成數據 (測試):"
    echo "   python manage.py simulate_ocean_data"
    echo "   python manage.py simulate_ocean_data --count=10"
    echo ""
    echo "📚 詳細文檔:"
    echo "   - QUICKSTART.md      (快速開始)"
    echo "   - REALTIME_GUIDE.md  (完整指南)"
    echo ""
}

# 主程序
main() {
    check_requirements
    check_database
    
    echo ""
    echo -e "${GREEN}✓ 環境檢查完成！${NC}"
    
    show_help
    
    echo ""
    echo "🚀 啟動服務..."
    echo ""
    
    # 創建必要的目錄
    mkdir -p logs
    
    # 啟動 Django (前台)
    echo "1️⃣  啟動 Django 開發伺服器..."
    python manage.py runserver 0.0.0.0:8000 &
    DJ_PID=$!
    sleep 2
    
    # 啟動 Celery Worker (後台)
    echo "2️⃣  啟動 Celery Worker..."
    celery -A config worker -l info > logs/celery_worker.log 2>&1 &
    WORKER_PID=$!
    sleep 2
    
    # 啟動 Celery Beat (後台)
    echo "3️⃣  啟動 Celery Beat..."
    celery -A config beat -l info > logs/celery_beat.log 2>&1 &
    BEAT_PID=$!
    sleep 2
    
    echo ""
    echo -e "${GREEN}✓ 所有服務已啟動！${NC}"
    echo ""
    echo "進程 PID:"
    echo "  Django:   $DJ_PID"
    echo "  Worker:   $WORKER_PID"
    echo "  Beat:     $BEAT_PID"
    echo ""
    echo "⏹️  停止服務，按 Ctrl+C"
    echo ""
    
    # 等待中斷
    wait
}

# 清理函數
cleanup() {
    echo ""
    echo -e "${YELLOW}正在停止服務...${NC}"
    kill $DJ_PID $WORKER_PID $BEAT_PID 2>/dev/null
    echo -e "${GREEN}✓ 服務已停止${NC}"
}

# 設置中斷信號處理
trap cleanup SIGINT SIGTERM

# 運行主程序
main
