# Django Admin 設定完成摘要

## ✅ 已完成設定

### 1. Django Admin 整合
- **位置**: `http://127.0.0.1:8000/panel/system-admin/`
- **功能**: 已整合到您的自訂後台 (`/panel/`) 中

### 2. URL 設定
修改檔案：`config/urls.py`
```python
# Django Admin (用於管理 Celery Beat 定時任務)
path('panel/system-admin/', admin.site.urls),
```

### 3. 建立的文件
1. **DJANGO_ADMIN_GUIDE.md** - Django Admin 完整使用指南
2. **create_superuser.py** - 快速建立超級使用者的腳本

---

## 🚀 下一步：建立超級使用者

### 方法 1：使用腳本（推薦）

```powershell
cd C:\Users\wesley\OneDrive\桌面\python全端開發\ocean_monitor
.\venv\Scripts\activate
python create_superuser.py
```

### 方法 2：使用 Django 指令

```powershell
cd C:\Users\wesley\OneDrive\桌面\python全端開發\ocean_monitor
.\venv\Scripts\activate
python manage.py createsuperuser --settings=config.settings.development
```

---

## 📖 使用步驟

### 1. 啟動 Django 伺服器
```powershell
cd C:\Users\wesley\OneDrive\桌面\python全端開發\ocean_monitor
.\venv\Scripts\activate
python manage.py runserver --settings=config.settings.development
```

### 2. 訪問 Django Admin
打開瀏覽器：`http://127.0.0.1:8000/panel/system-admin/`

### 3. 登入
使用剛才建立的超級使用者帳號密碼

### 4. 管理定時任務
在 **PERIODIC TASKS** 區塊中：
- **Intervals** - 建立時間間隔（如每 5 分鐘）
- **Crontabs** - 建立 cron 排程（如每天凌晨 2 點）
- **Periodic tasks** - 新增/編輯定時任務

---

## 🎯 可用的 Celery 任務

| 任務名稱 | 說明 |
|---------|------|
| `station_data.tasks.update_ocean_data_from_source` | 更新海洋數據 |
| `station_data.tasks.check_ocean_data_alerts` | 檢查數據異常 |
| `station_data.tasks.generate_daily_statistics` | 產生每日統計 |
| `station_data.tasks.send_data_alert_notification` | 發送異常通知（可指定使用者） |

---

## 💡 範例：新增定時任務

### 每 10 分鐘更新海洋數據

1. 進入 Django Admin → **Intervals** → **Add interval**
   - Every: `10`
   - Period: `minutes`
   - 儲存

2. 進入 **Periodic tasks** → **Add periodic task**
   - Name: `每 10 分鐘更新數據`
   - Task: `station_data.tasks.update_ocean_data_from_source`
   - Interval: 選擇 `every 10 minutes`
   - Enabled: ✅ 勾選
   - 儲存

完成！任務會立即開始執行（無需重啟服務）

---

## 📚 詳細文件

- **DJANGO_ADMIN_GUIDE.md** - Django Admin 完整使用指南
- **CELERY_GUIDE.md** - Celery 定時任務啟動指南

---

## ❓ 常見問題

### Q: Django Admin 和自訂後台（admin_panel）有什麼不同？

**Django Admin** (`/panel/system-admin/`)：
- Django 內建的後台管理介面
- 主要用於管理資料庫模型和 Celery Beat 定時任務
- 功能完整但介面較為通用

**自訂後台** (`/panel/`)：
- 您自己開發的管理介面
- 可以完全自訂外觀和功能
- 針對專案需求客製化

### Q: 我應該使用哪一個？

建議兩者搭配使用：
- **Celery 定時任務管理** → 使用 Django Admin（`/panel/system-admin/`）
- **日常業務操作（測站管理、數據查看等）** → 使用自訂後台（`/panel/`）

### Q: 可以在自訂後台加入定時任務管理嗎？

可以！您可以透過程式碼操作 django-celery-beat 模型：

```python
from django_celery_beat.models import PeriodicTask, IntervalSchedule

# 建立間隔排程
schedule, created = IntervalSchedule.objects.get_or_create(
    every=10,
    period=IntervalSchedule.MINUTES,
)

# 建立定時任務
PeriodicTask.objects.create(
    interval=schedule,
    name='每 10 分鐘更新數據',
    task='station_data.tasks.update_ocean_data_from_source',
)
```

詳細範例請參考 CELERY_GUIDE.md 的「程式碼管理範例」章節。

---

## 🎉 完成！

您現在可以透過 `http://127.0.0.1:8000/panel/system-admin/` 管理所有 Celery 定時任務了！
