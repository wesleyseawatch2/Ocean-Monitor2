# Django Admin 使用指南

## 什麼是 Django Admin？

Django Admin 是 Django 內建的後台管理介面，提供：
- 資料庫模型的 CRUD 操作（新增、讀取、更新、刪除）
- 使用者權限管理
- **django-celery-beat 定時任務管理**（動態新增/修改排程）

## 存取位置

您的專案已將 Django Admin 整合到自訂後台中：

```
http://127.0.0.1:8000/panel/system-admin/
```

## 建立超級使用者

第一次使用需要建立管理員帳號：

```powershell
# 進入專案目錄
cd C:\Users\wesley\OneDrive\桌面\python全端開發\ocean_monitor

# 啟動虛擬環境
.\venv\Scripts\activate

# 建立超級使用者
python manage.py createsuperuser --settings=config.settings.development
```

按照提示輸入：
- Username（使用者名稱）
- Email（電子郵件，可留空）
- Password（密碼，至少 8 位）

## 使用 Django Admin 管理定時任務

### 1. 登入 Django Admin

1. 啟動 Django 開發伺服器：
   ```powershell
   python manage.py runserver --settings=config.settings.development
   ```

2. 打開瀏覽器訪問：`http://127.0.0.1:8000/panel/system-admin/`

3. 使用剛才建立的超級使用者登入

### 2. 管理定時任務

登入後，您會看到 **PERIODIC TASKS** 區塊，包含：

#### Intervals（時間間隔）
- 定義重複間隔（如：每 30 秒、每 5 分鐘）
- 範例：
  - Every: `30`
  - Period: `seconds`

#### Crontabs（Cron 表達式）
- 使用 cron 格式定義排程
- 範例：
  - Minute: `0`（每小時的第 0 分）
  - Hour: `*/2`（每 2 小時）
  - Day of week: `*`（每天）
  - Day of month: `*`（每月）
  - Month of year: `*`（每年）

#### Periodic tasks（定時任務）
- 新增/編輯定時任務
- 欄位說明：
  - **Name**: 任務名稱（自訂）
  - **Task (registered)**: 選擇已註冊的 Celery 任務
  - **Enabled**: 啟用/停用
  - **Interval**: 選擇時間間隔（或使用 Crontab）
  - **Crontab**: 選擇 cron 排程（或使用 Interval）
  - **Arguments**: JSON 格式的參數，如 `[123]`
  - **Keyword arguments**: JSON 格式的關鍵字參數，如 `{"user_id": 5}`

### 3. 可用的任務清單

您的專案中已註冊以下 Celery 任務：

| 任務名稱 | 說明 | 參數 |
|---------|------|------|
| `station_data.tasks.update_ocean_data_from_source` | 從資料源更新海洋數據 | 無 |
| `station_data.tasks.check_ocean_data_alerts` | 檢查數據異常並發送警告 | 無 |
| `station_data.tasks.generate_daily_statistics` | 產生每日統計報告 | 無 |
| `station_data.tasks.send_data_alert_notification` | 發送數據異常通知（可指定使用者） | `user_id` (選填) |

### 4. 新增定時任務範例

#### 範例 1：每 5 分鐘更新一次海洋數據

1. 先建立 Interval：
   - 點擊 **Intervals** → **Add interval**
   - Every: `5`
   - Period: `minutes`
   - 儲存

2. 建立 Periodic task：
   - 點擊 **Periodic tasks** → **Add periodic task**
   - Name: `每 5 分鐘更新海洋數據`
   - Task (registered): `station_data.tasks.update_ocean_data_from_source`
   - Interval: 選擇剛才建立的 `every 5 minutes`
   - Enabled: 勾選
   - 儲存

#### 範例 2：每天凌晨 2 點產生統計報告

1. 先建立 Crontab：
   - 點擊 **Crontabs** → **Add crontab**
   - Minute: `0`
   - Hour: `2`
   - Day of week: `*`
   - Day of month: `*`
   - Month of year: `*`
   - 儲存

2. 建立 Periodic task：
   - 點擊 **Periodic tasks** → **Add periodic task**
   - Name: `每日統計報告（凌晨 2 點）`
   - Task (registered): `station_data.tasks.generate_daily_statistics`
   - Crontab: 選擇剛才建立的 `0 2 * * *`
   - Enabled: 勾選
   - 儲存

#### 範例 3：每小時為特定使用者檢查異常

1. 建立 Periodic task：
   - Name: `每小時檢查異常（使用者 5）`
   - Task (registered): `station_data.tasks.send_data_alert_notification`
   - Interval: 選擇 `every 1 hour`（需先建立）
   - Keyword arguments: `{"user_id": 5}`
   - Enabled: 勾選
   - 儲存

## 優點：動態排程

使用 Django Admin 管理定時任務的優點：

1. **無需重啟服務**：新增/修改排程後立即生效
2. **視覺化管理**：透過網頁介面操作，不需修改程式碼
3. **歷史記錄**：可查看任務執行記錄
4. **權限控制**：可設定哪些使用者能管理排程

## 監控任務執行

在 Celery Worker 和 Celery Beat 的 Terminal 視窗中，您可以看到：

```
[2025-12-02 10:00:00] Task station_data.tasks.update_ocean_data_from_source[...] received
[2025-12-02 10:00:01] Task station_data.tasks.update_ocean_data_from_source[...] succeeded
```

## 注意事項

1. **Celery Beat 必須使用資料庫排程器**：
   ```powershell
   celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
   ```

2. **靜態排程 vs 動態排程**：
   - 靜態排程（`config/settings/base.py` 中的 `CELERY_BEAT_SCHEDULE`）：需重啟服務
   - 動態排程（Django Admin）：立即生效

3. **建議**：
   - 固定的、長期的排程 → 靜態排程
   - 臨時的、需經常調整的排程 → 動態排程

## 疑難排解

### 問題 1：找不到任務
確認 Celery Worker 已啟動並能看到任務註冊：
```powershell
celery -A config worker -l info --pool=solo
```

### 問題 2：任務沒有執行
檢查：
1. Celery Beat 是否使用 `--scheduler django_celery_beat.schedulers:DatabaseScheduler`
2. Periodic task 的 **Enabled** 是否勾選
3. Celery Worker 和 Beat 的 Terminal 是否有錯誤訊息

### 問題 3：忘記超級使用者密碼
重新建立：
```powershell
python manage.py createsuperuser --settings=config.settings.development
```

## 擴展功能

### 自訂 Django Admin 介面

您可以在 `admin_panel/admin.py` 中自訂 Admin 介面：

```python
from django.contrib import admin
from data_ingestion.models import Station, Reading

@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ['station_name', 'device_model', 'location', 'install_date']
    search_fields = ['station_name', 'location']
    list_filter = ['install_date']

@admin.register(Reading)
class ReadingAdmin(admin.ModelAdmin):
    list_display = ['station', 'timestamp', 'temperature', 'salinity', 'ph']
    list_filter = ['station', 'timestamp']
    date_hierarchy = 'timestamp'
```

這樣就能在 Django Admin 中管理測站和數據記錄了！

## 總結

- **Django Admin 位置**：`http://127.0.0.1:8000/panel/system-admin/`
- **主要用途**：管理 Celery Beat 定時任務
- **優勢**：動態排程、無需重啟、視覺化管理
- **下一步**：建立超級使用者並登入試用！
