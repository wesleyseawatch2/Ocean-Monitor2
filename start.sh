#!/bin/bash

# Zeabur 啟動腳本

echo "=== 開始部署 ==="

# 1. 收集靜態檔案
echo ">>> 收集靜態檔案..."
python manage.py collectstatic --noinput --clear
if [ $? -eq 0 ]; then
    echo "✓ 靜態檔案收集完成"
    ls -la staticfiles/ | head -20
else
    echo "✗ 靜態檔案收集失敗"
    exit 1
fi

# 2. 執行資料庫遷移
echo ">>> 執行資料庫遷移..."
python manage.py migrate --noinput
if [ $? -eq 0 ]; then
    echo "✓ 資料庫遷移完成"
else
    echo "✗ 資料庫遷移失敗"
    exit 1
fi

# 3. 啟動 Daphne
echo ">>> 啟動 Daphne 伺服器..."
echo "監聽 Port: ${PORT:-8080}"
daphne -b 0.0.0.0 -p ${PORT:-8080} config.asgi:application
