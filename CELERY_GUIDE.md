# Celery 定時任務啟動指南（使用 django-celery-beat）

## 📋 功能特色

本專案使用 **django-celery-beat** 實現動態定時任務管理：

✅ **動態管理排程** - 透過 Django Admin 或程式碼新增/修改/刪除定時任務
✅ **即時生效** - 修改後不需重啟 Celery Beat
✅ **資料庫儲存** - 排程資訊存放在資料庫中，易於備份和管理
✅ **支援多種排程類型** - Crontab、Interval、Solar、Clocked

---

## 🎯 快速開始：使用 Django Admin 管理定時任務

**推薦閱讀**: 請先查看 [DJANGO_ADMIN_GUIDE.md](DJANGO_ADMIN_GUIDE.md) 了解如何透過網頁介面管理定時任務

Django Admin 位置：`http://127.0.0.1:8000/panel/system-admin/`

---

## 系統架構

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Celery Beat 運作原理                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌────────────┐    定時發送任務    ┌────────────┐                  │
│   │   Celery   │ ────────────────> │   Redis    │                  │
│   │    Beat    │                   │  (Broker)  │                  │
│   │  (排程器)   │                   │            │                  │
│   └────────────┘                   └─────┬──────┘                  │
│                                          │                          │
│                                          ▼                          │
│                                    ┌────────────┐                   │
│                                    │   Celery   │                   │
│                                    │   Worker   │                   │
│                                    │  (執行器)   │                   │
│                                    └────────────┘                   │
│                                                                     │
│   類比：                                                            │
│   • Beat 像是「鬧鐘」，到時間就發送任務                             │
│   • Worker 像是「員工」，接收並執行任務                             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 已設定的定時任務

### 1. 更新海洋數據
- **任務名稱**: `update_ocean_data_from_source`
- **執行頻率**: 每小時（整點執行）
- **測試頻率**: 每 1 分鐘（開發測試用）
- **功能**: 從資料來源更新海洋數據

### 2. 檢查數據異常
- **任務名稱**: `check_ocean_data_alerts`
- **執行頻率**: 每 6 小時
- **功能**: 檢查溫度、pH、溶氧量等異常數據

### 3. 每日統計報告
- **任務名稱**: `generate_daily_statistics`
- **執行頻率**: 每天早上 8 點
- **功能**: 產生當日數據統計報告

## 啟動步驟

### 前置準備
確保以下服務已啟動：
1. ✅ Redis 服務（Memurai）
2. ✅ Django 開發伺服器

### Windows PowerShell 啟動方式

#### Terminal 1: Redis (Memurai)
```powershell
# 檢查 Memurai 服務狀態
sc query Memurai

# 如果未啟動，啟動服務
net start Memurai
```

#### Terminal 2: Django 開發伺服器
```powershell
cd c:\Users\wesley\OneDrive\桌面\python全端開發\ocean_monitor
.\venv\Scripts\activate
python manage.py runserver
```

#### Terminal 3: Celery Worker
```powershell
cd c:\Users\wesley\OneDrive\桌面\python全端開發\ocean_monitor
.\venv\Scripts\activate
.\venv\Scripts\celery.exe -A config worker -l info --pool=solo
```

#### Terminal 4: Celery Beat（使用資料庫排程器）
```powershell
cd c:\Users\wesley\OneDrive\桌面\python全端開發\ocean_monitor
.\venv\Scripts\activate
.\venv\Scripts\celery.exe -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

💡 **注意**：加上 `--scheduler django_celery_beat.schedulers:DatabaseScheduler` 參數是為了確保使用資料庫排程器

## 測試方式

### 方法 1: 執行測試腳本（推薦）
```powershell
cd c:\Users\wesley\OneDrive\桌面\python全端開發\ocean_monitor
.\venv\Scripts\python.exe test_celery_tasks.py
```

### 方法 2: 手動觸發任務（Django Shell）
```powershell
python manage.py shell
```

```python
from station_data.tasks import update_ocean_data_from_source

# 手動執行任務
result = update_ocean_data_from_source()
print(result)
```

### 方法 3: 等待定時任務自動執行
啟動 Celery Beat 後，觀察 Terminal 3 (Worker) 的輸出：
- 測試任務每 1 分鐘會自動執行
- 觀察是否出現 `[定時任務] 開始更新海洋數據...`

## Celery Beat 輸出範例

啟動成功後，應該看到類似輸出：

```
celery beat v5.6.0 (dawn-chorus) is starting.
__    -    ... __   -        _
LocalTime -> 2025-12-02 14:30:00
Configuration ->
    . broker -> redis://127.0.0.1:6379/1
    . loader -> celery.loaders.app.AppLoader
    . scheduler -> celery.beat.PersistentScheduler
    . db -> celerybeat-schedule
    . logfile -> [stderr]@%INFO
    . maxinterval -> 5.00 minutes (300s)

[2025-12-02 14:30:00] beat: Starting...
[2025-12-02 14:30:00] Scheduler: Sending due task test-update-every-minute
[2025-12-02 14:31:00] Scheduler: Sending due task test-update-every-minute
```

## 排程設定說明

在 `config/settings/base.py` 中的 `CELERY_BEAT_SCHEDULE`：

| 設定方式 | 說明 | 範例 |
|---------|------|------|
| `60.0` | 每 60 秒執行 | `'schedule': 60.0` |
| `crontab(minute=0)` | 每小時整點 | 0:00, 1:00, 2:00... |
| `crontab(hour=8, minute=0)` | 每天早上 8 點 | 08:00 |
| `crontab(minute='*/15')` | 每 15 分鐘 | 0, 15, 30, 45 分 |
| `crontab(hour='*/6')` | 每 6 小時 | 0, 6, 12, 18 點 |
| `crontab(day_of_week=1)` | 每週一 | 星期一執行 |

## 常見 crontab 範例

```python
# 每天早上 9 點
crontab(hour=9, minute=0)

# 每天早上 9 點和下午 5 點
crontab(hour='9,17', minute=0)

# 每小時的第 0 分鐘
crontab(minute=0)

# 每 30 分鐘
crontab(minute='*/30')

# 每週一早上 9 點
crontab(hour=9, minute=0, day_of_week=1)

# 每月 1 號早上 9 點
crontab(hour=9, minute=0, day_of_month=1)
```

## 整合資料來源

### 串接 Google Sheets

1. 安裝套件：
```powershell
pip install gspread oauth2client
```

2. 設定 Google Service Account
   - 前往 [Google Cloud Console](https://console.cloud.google.com/)
   - 建立專案並啟用 Google Sheets API
   - 建立 Service Account 並下載 JSON 憑證
   - 在 Google Sheets 中分享給 service account email

3. 修改 `station_data/tasks.py` 中的 `fetch_from_google_sheets()` 函數

### 串接外部資料庫

1. 安裝對應驅動：
```powershell
# PostgreSQL
pip install psycopg2-binary

# MySQL
pip install mysqlclient

# SQL Server
pip install pyodbc
```

2. 修改 `station_data/tasks.py` 中的 `fetch_from_database()` 函數

### 串接外部 API

1. 安裝 requests：
```powershell
pip install requests
```

2. 修改 `station_data/tasks.py` 中的 `fetch_from_external_api()` 函數

## 監控與除錯

### 查看 Celery Worker 日誌
觀察 Terminal 3 的輸出，應該看到：
```
[定時任務] 開始更新海洋數據...
[定時任務] 新增數據: 21 - ChaoJingCR1000X
```

### 查看 Celery Beat 日誌
觀察 Terminal 4 的輸出，應該看到：
```
[2025-12-02 14:31:00] Scheduler: Sending due task test-update-every-minute
```

### 查看 Redis 狀態
```powershell
& "C:\Program Files\Memurai\memurai-cli.exe" ping
& "C:\Program Files\Memurai\memurai-cli.exe" info
```

## 停止服務

```powershell
# 在各個 Terminal 按 Ctrl+C 停止服務
# 或直接關閉 Terminal 視窗
```

## 注意事項

⚠️ **重要提醒**：
1. 測試任務（`test-update-every-minute`）會每分鐘執行，正式環境請註解或移除
2. 確保 Redis 服務正在運行，否則 Celery 無法啟動
3. Celery Beat 會產生 `celerybeat-schedule` 檔案，已加入 `.gitignore`
4. 修改排程設定後，需要重新啟動 Celery Beat

## 生產環境部署建議

### 移除測試任務
在 `config/settings/base.py` 中註解或刪除：
```python
# 'test-update-every-minute': {
#     'task': 'station_data.tasks.update_ocean_data_from_source',
#     'schedule': 60.0,
# },
```

### 使用 Supervisor 管理服務
建議使用 Supervisor 或 systemd 管理 Celery Worker 和 Beat

### 設定日誌輪替
配置 logrotate 避免日誌檔過大

## 疑難排解

### Q: Celery Beat 無法啟動
**A**: 檢查 Redis 是否正在運行：
```powershell
sc query Memurai
```

### Q: 任務沒有執行
**A**:
1. 確認 Celery Worker 正在運行
2. 檢查 Worker 日誌是否有錯誤
3. 確認任務名稱正確（`app_name.tasks.function_name`）

### Q: 修改排程後沒有生效
**A**:
1. 刪除 `celerybeat-schedule` 檔案
2. 重新啟動 Celery Beat

## 🎯 使用 Django Admin 管理排程

### 1. 進入 Django Admin

訪問：http://127.0.0.1:8000/admin/

登入後，你會看到 **PERIODIC TASKS** 區塊：

```
┌─────────────────────────────────────────────────────────────┐
│              Django Admin - PERIODIC TASKS                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📁 Clocked schedules      一次性排程（指定日期時間）        │
│  📁 Crontabs              Cron 表達式（分/時/日/月/週）      │
│  📁 Intervals             間隔時間（每 N 秒/分/時執行）       │
│  📁 Periodic tasks        定時任務（主要設定）               │
│  📁 Solar events          太陽事件（日出/日落觸發）           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2. 建立間隔排程（Interval）

1. 點選 **Intervals** → **Add interval**
2. 設定：
   - **Every**: 5
   - **Period**: minutes
3. 點選 **Save**

### 3. 建立定時任務（Periodic Task）

1. 點選 **Periodic tasks** → **Add periodic task**
2. 設定：
   - **Name**: 每5分鐘檢查數據異常
   - **Task (registered)**: `station_data.tasks.send_data_alert_notification`
   - **Interval Schedule**: 選擇剛剛建立的 "every 5 minutes"
   - **Enabled**: ✅ 打勾
   - **Arguments** (JSON): `[]`
   - **Keyword arguments** (JSON): `{"user_id": null}` （null 表示全域通知）
3. 點選 **Save**

### 4. 建立 Crontab 排程

如果要使用 Cron 表達式，先建立 Crontab：

1. 點選 **Crontabs** → **Add crontab**
2. 設定：
   - **Minute**: 0
   - **Hour**: */6 （每 6 小時）
   - **Day of week**: * （每天）
   - **Day of month**: * （每月）
   - **Month of year**: * （每年）
   - **Timezone**: Asia/Taipei
3. 點選 **Save**

然後在 Periodic tasks 中使用這個 Crontab Schedule

### 5. 即時生效

✨ **重點**：儲存後，Celery Beat 會自動偵測到新任務並開始執行，**不需要重啟服務**！

## 💡 動態排程的優勢

### 靜態設定 vs 動態設定對比

| 特性 | 靜態設定（settings.py） | 動態設定（django-celery-beat） |
|------|------------------------|-------------------------------|
| 修改方式 | 修改程式碼 | Django Admin / API |
| 是否需要重啟 | ✅ 需要 | ❌ 不需要 |
| 適用場景 | 固定的全域任務 | 使用者自訂、臨時任務 |
| 易於管理 | ❌ | ✅ |

### 本專案的排程策略

我們採用 **混合模式**：

1. **靜態排程**（`CELERY_BEAT_SCHEDULE`）
   - 固定的全域任務
   - 例如：每小時更新數據、每天產生統計

2. **動態排程**（Django Admin）
   - 使用者自訂通知頻率
   - 臨時測試任務
   - 一次性任務

## 📝 透過程式碼管理排程

### 範例：建立使用者專屬的通知任務

```python
from django_celery_beat.models import PeriodicTask, IntervalSchedule
import json

# 1. 建立間隔排程：每 30 分鐘
schedule, created = IntervalSchedule.objects.get_or_create(
    every=30,
    period=IntervalSchedule.MINUTES,
)

# 2. 建立定時任務
task = PeriodicTask.objects.create(
    name=f'user_{user_id}_data_alert',  # 任務名稱（必須唯一）
    task='station_data.tasks.send_data_alert_notification',  # 任務路徑
    interval=schedule,  # 使用間隔排程
    args=json.dumps([]),  # 位置參數
    kwargs=json.dumps({'user_id': user_id}),  # 關鍵字參數
    enabled=True,  # 啟用
)

print(f"已建立任務：{task.name}")
```

### 範例：更新排程頻率

```python
from django_celery_beat.models import PeriodicTask, IntervalSchedule

# 找到任務
task = PeriodicTask.objects.get(name=f'user_{user_id}_data_alert')

# 建立新的間隔（每 1 小時）
new_schedule, _ = IntervalSchedule.objects.get_or_create(
    every=1,
    period=IntervalSchedule.HOURS,
)

# 更新任務
task.interval = new_schedule
task.save()

print(f"任務 {task.name} 已更新為每小時執行")
```

### 範例：停用任務

```python
from django_celery_beat.models import PeriodicTask

# 方法 1：停用任務
task = PeriodicTask.objects.get(name=f'user_{user_id}_data_alert')
task.enabled = False
task.save()

# 方法 2：刪除任務
PeriodicTask.objects.filter(name=f'user_{user_id}_data_alert').delete()
```

## 🔄 任務類型說明

### 1. Interval（間隔）
固定間隔時間執行

```python
# 每 30 秒
schedule = IntervalSchedule.objects.create(
    every=30,
    period=IntervalSchedule.SECONDS,
)

# 每 5 分鐘
schedule = IntervalSchedule.objects.create(
    every=5,
    period=IntervalSchedule.MINUTES,
)

# 每 2 小時
schedule = IntervalSchedule.objects.create(
    every=2,
    period=IntervalSchedule.HOURS,
)
```

### 2. Crontab（Cron 表達式）
使用 Cron 語法，更靈活

```python
from django_celery_beat.models import CrontabSchedule

# 每天早上 9 點
schedule = CrontabSchedule.objects.create(
    minute='0',
    hour='9',
    day_of_week='*',
    day_of_month='*',
    month_of_year='*',
)

# 每週一早上 9 點
schedule = CrontabSchedule.objects.create(
    minute='0',
    hour='9',
    day_of_week='1',
    day_of_month='*',
    month_of_year='*',
)

# 每 15 分鐘
schedule = CrontabSchedule.objects.create(
    minute='*/15',
    hour='*',
    day_of_week='*',
    day_of_month='*',
    month_of_year='*',
)
```

### 3. Clocked（一次性）
在特定時間執行一次

```python
from django_celery_beat.models import ClockedSchedule
from datetime import datetime, timedelta

# 10 分鐘後執行一次
schedule = ClockedSchedule.objects.create(
    clocked_time=datetime.now() + timedelta(minutes=10)
)

# 使用在 PeriodicTask 中
PeriodicTask.objects.create(
    name='one_time_task',
    task='station_data.tasks.update_ocean_data_from_source',
    clocked=schedule,
    one_off=True,  # 執行一次後自動停用
)
```

## 注意事項（更新）

⚠️ **重要提醒**：

1. **靜態排程**：測試任務（`test-update-every-2-minutes`）會每 2 分鐘執行，正式環境請註解或移除
2. **動態排程**：透過 Django Admin 建立的任務會即時生效，不需要重啟
3. 確保 Redis 服務正在運行
4. Celery Beat 會產生 `celerybeat-schedule` 檔案（資料庫排程的快取），已加入 `.gitignore`
5. 啟動 Celery Beat 時務必加上 `--scheduler django_celery_beat.schedulers:DatabaseScheduler` 參數

## 參考資料

- [Celery 官方文檔](https://docs.celeryproject.org/)
- [Celery Beat 排程設定](https://docs.celeryproject.org/en/stable/userguide/periodic-tasks.html)
- [django-celery-beat 文檔](https://github.com/celery/django-celery-beat)
- [Google Sheets API](https://developers.google.com/sheets/api)
