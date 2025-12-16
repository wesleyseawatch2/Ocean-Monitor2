# WebSocket 即時更新設定說明

## 已完成的設定

### 1. 後端 WebSocket Consumer
- 檔案：`station_data/consumers.py`
- 功能：處理 WebSocket 連接並發送即時感測器資料
- 支援單一測站和所有測站的即時資料推送

### 2. WebSocket URL Routing
- 檔案：`station_data/routing.py`
- WebSocket 端點：
  - `ws://localhost:8000/ws/stations/readings/` - 所有測站的即時資料
  - `ws://localhost:8000/ws/stations/<station_id>/` - 特定測站的即時資料

### 3. ASGI 配置
- 檔案：`config/asgi.py`
- 已啟用 WebSocket 支援
- 使用 AuthMiddlewareStack 和 URLRouter

### 4. 前端 JavaScript
- 檔案：`station_data/static/realtime.js`
- 已從 HTTP 輪詢改為 WebSocket 連接
- 自動重連機制（最多 5 次）
- 連線狀態指示器

### 5. Django Settings
- 檔案：`config/settings/base.py`
- 已添加 `CHANNEL_LAYERS` 配置
- 使用 Redis 作為 WebSocket 消息層

### 6. 依賴套件
- ✅ channels (4.3.2)
- ✅ channels_redis (4.3.0)
- ✅ redis (7.1.0)

## 啟動步驟

### 1. 確保 Redis 正在運行
```bash
# Windows (如果使用 WSL 或 Docker)
docker run -p 6379:6379 redis

# 或使用本地 Redis 服務
```

### 2. 啟動 Django 服務器（使用 Daphne 支援 WebSocket）
```bash
# 方法 1: 使用 Daphne（推薦）
source venv/Scripts/activate
daphne -b 0.0.0.0 -p 8000 config.asgi:application

# 方法 2: 使用 Django runserver（開發環境，Django 4.2+ 支援 ASGI）
python manage.py runserver
```

### 3. 啟動 Celery Worker（如果需要後台任務）
```bash
source venv/Scripts/activate
celery -A config worker -l info
```

### 4. 啟動 Celery Beat（如果需要定時任務）
```bash
source venv/Scripts/activate
celery -A config beat -l info
```

## 測試 WebSocket 連接

1. 打開瀏覽器訪問測站頁面
2. 打開瀏覽器開發者工具（F12）
3. 查看 Console 標籤，應該會看到：
   ```
   [WebSocket] DOMContentLoaded 觸發
   [WebSocket] 正在連接: ws://localhost:8000/ws/stations/1/
   [WebSocket] 連接成功
   [WebSocket] 收到初始資料
   ```
4. 頁面右上角應該顯示綠色指示器「已連線」

## 如何觸發即時更新

WebSocket 會在連接時自動發送當前資料。要觸發即時更新，需要：

### 方法 1: 使用 Celery 任務自動產生新資料
當 Celery 任務產生新的感測器讀數時，可以在 `station_data/tasks.py` 中添加：

```python
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def update_ocean_data_from_source():
    # ... 產生新資料的程式碼 ...

    # 發送 WebSocket 更新
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'station_{station_id}',
        {
            'type': 'sensor_reading_update',
            'data': {
                'station_id': station.id,
                'timestamp': reading.timestamp.isoformat(),
                'temperature': float(reading.temperature),
                # ... 其他欄位
            }
        }
    )
```

### 方法 2: 手動在 Django Shell 中測試
```python
python manage.py shell

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import datetime

channel_layer = get_channel_layer()
async_to_sync(channel_layer.group_send)(
    'station_1',  # 測站 1 的群組
    {
        'type': 'sensor_reading_update',
        'data': {
            'station_id': 1,
            'timestamp': datetime.now().isoformat(),
            'temperature': 25.5,
            'ph': 8.2,
            'dissolved_oxygen': 7.5,
            'salinity': 35.0,
        }
    }
)
```

## 故障排除

### WebSocket 連接失敗
1. 確認 Redis 正在運行
2. 檢查 `CHANNEL_LAYERS` 配置中的 Redis URI
3. 確保使用 Daphne 或 Django 4.2+ runserver

### 連接成功但沒有收到資料
1. 檢查資料庫中是否有測站和讀數資料
2. 查看 Django 日誌確認 WebSocket consumer 是否正常運行

### 頁面顯示「連線中斷」
1. 檢查 Redis 連接
2. 查看瀏覽器 Console 的錯誤訊息
3. 檢查伺服器日誌

## 從 HTTP 輪詢切換到 WebSocket 的好處

1. **即時性更好**：資料產生後立即推送，不需要等待輪詢週期
2. **伺服器負載更低**：不需要每 5 秒處理一次 HTTP 請求
3. **網路流量更小**：只在有新資料時才傳輸
4. **用戶體驗更好**：連線狀態清楚顯示，斷線自動重連

## 注意事項

- WebSocket 連接需要保持開啟，關閉分頁會自動斷開
- 生產環境建議使用 Nginx 反向代理並配置 WebSocket 支援
- Redis 需要持續運行以支援 WebSocket 消息層
