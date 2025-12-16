#!/bin/bash

echo "=== 靜態檔案診斷腳本 ==="
echo ""

# 1. 檢查環境變數
echo "1. 環境變數:"
echo "   DJANGO_ENV = ${DJANGO_ENV:-未設定}"
export DJANGO_ENV=production
echo "   已設定 DJANGO_ENV=production"
echo ""

# 2. 檢查 Django settings
echo "2. Django Settings:"
python -c "
import os
os.environ['DJANGO_ENV'] = 'production'
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.production'
import django
django.setup()
from django.conf import settings

print(f'   Settings Module: {os.environ.get(\"DJANGO_SETTINGS_MODULE\")}')
print(f'   DEBUG: {settings.DEBUG}')
print(f'   STATIC_URL: {settings.STATIC_URL}')
print(f'   STATIC_ROOT: {settings.STATIC_ROOT}')

if hasattr(settings, 'STORAGES'):
    backend = settings.STORAGES.get('staticfiles', {}).get('BACKEND', 'Not set')
    print(f'   Staticfiles Backend: {backend}')

whitenoise_mw = any('whitenoise' in mw.lower() for mw in settings.MIDDLEWARE)
print(f'   WhiteNoise Middleware: {\"Yes\" if whitenoise_mw else \"No\"}')"

echo ""

# 3. 檢查靜態檔案目錄
echo "3. 靜態檔案目錄:"
if [ -d "staticfiles" ]; then
    echo "   staticfiles/ 目錄存在"
    echo "   檔案數量: $(find staticfiles -type f | wc -l)"
    echo ""
    echo "   realtime 檔案:"
    ls -lh staticfiles/realtime.* 2>/dev/null || echo "   [錯誤] realtime.* 檔案不存在!"
else
    echo "   [錯誤] staticfiles/ 目錄不存在!"
fi

echo ""

# 4. 重新收集靜態檔案
echo "4. 重新收集靜態檔案:"
python manage.py collectstatic --noinput --clear
if [ $? -eq 0 ]; then
    echo "   [成功] 靜態檔案收集完成"
else
    echo "   [失敗] 靜態檔案收集失敗"
    exit 1
fi

echo ""

# 5. 再次檢查
echo "5. 收集後檢查:"
ls -lh staticfiles/realtime.* 2>/dev/null && echo "   [成功] realtime 檔案存在" || echo "   [失敗] realtime 檔案仍然不存在"

echo ""
echo "=== 診斷完成 ==="
echo ""
echo "如果一切正常,請執行: bash start.sh"
