#!/bin/bash
# 生產環境資料庫遷移腳本
# 用途：修復 station_id 欄位缺失問題

echo "========================================"
echo "Ocean Monitor - 資料庫遷移"
echo "========================================"
echo ""

# 1. 檢查當前遷移狀態
echo "📋 檢查遷移狀態..."
python manage.py showmigrations station_data

echo ""
echo "----------------------------------------"

# 2. 執行遷移
echo "🔧 執行資料庫遷移..."
python manage.py migrate station_data

echo ""
echo "----------------------------------------"

# 3. 驗證遷移結果
echo "✅ 驗證遷移結果..."
python manage.py showmigrations station_data

echo ""
echo "========================================"
echo "遷移完成！請重啟 Django 應用："
echo "  sudo systemctl restart gunicorn"
echo "或"
echo "  supervisorctl restart ocean_monitor"
echo "========================================"
