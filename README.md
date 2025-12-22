# Ocean Monitor Web

基於 Django 的海洋數據監測與可視化系統，整合 WebSocket 即時推送、Celery 定時任務、Google Sheets 數據同步和 Gemini AI 分析。

## 專案架構

```
ocean_monitor/
├── config/                      # Django 專案設定
│   ├── settings/
│   │   ├── base.py             # 共用設定
│   │   ├── development.py      # 開發環境設定
│   │   └── production.py       # 生產環境設定
│   ├── urls.py                 # 主 URL 路由
│   ├── wsgi.py                 # WSGI 配置
│   ├── asgi.py                 # ASGI 配置 (WebSocket)
│   └── celery.py               # Celery 配置
├── apps/                       # 核心應用程式
│   └── core/
│       ├── accounts/           # 自訂使用者模型
│       ├── urls.py             # 通用登入路由
│       └── adapters.py         # allauth 自訂適配器
├── data_ingestion/             # 數據接收與儲存
│   ├── models.py               # Station、Reading、Trajectory Models
│   ├── admin.py                # 管理後台設定
│   └── management/commands/    # 管理命令
│       ├── setup_demo_stations.py         # 建立示範測站
│       ├── generate_trajectory_data.py    # 生成軌跡數據
│       └── reset_trajectory_data.py       # 重置軌跡數據
├── station_data/               # 測站數據展示與處理
│   ├── views.py                # 視圖邏輯
│   ├── urls.py                 # App URL 路由
│   ├── consumers.py            # WebSocket Consumers
│   ├── tasks.py                # Celery 定時任務
│   ├── simulation.py           # 數據模擬邏輯
│   └── management/commands/
│       └── simulate_ocean_data.py         # 生成模擬數據
├── admin_panel/                # 自訂管理後台
│   ├── views.py                # 後台視圖
│   └── urls.py                 # 後台路由
├── analysis_tools/             # 數據分析工具
│   ├── calculations.py         # 統計分析函數
│   ├── chart_helpers.py        # 圖表數據轉換
│   ├── gemini_service.py       # Gemini AI 服務
│   └── anonymizer.py           # 數據匿名化
├── templates/                  # HTML 模板
│   ├── base.html
│   ├── station_data/
│   ├── admin_panel/
│   └── account/
├── static/                     # 靜態檔案
└── manage.py                   # Django 管理腳本
```

## 資料庫架構

### 核心模型

#### User (自訂使用者模型)
- 擴展 Django AbstractUser
- 支援 Email/Username 雙重認證
- Google OAuth 社交登入

#### Station (測站)
| 欄位 | 類型 | 說明 |
|------|------|------|
| station_name | VARCHAR(100) | 測站名稱 |
| device_model | VARCHAR(50) | 設備型號 |
| location | VARCHAR(100) | 裝設地點 |
| install_date | DATE | 裝設日期 |
| latitude | DECIMAL(9,6) | 緯度 |
| longitude | DECIMAL(9,6) | 經度 |

#### Reading (數據記錄)
| 欄位 | 類型 | 說明 |
|------|------|------|
| station | ForeignKey | 關聯測站 |
| timestamp | DATETIME | 時間戳 |
| temperature | DECIMAL(5,2) | 溫度 (°C) |
| conductivity | DECIMAL(10,2) | 電導率 (uS/cm) |
| pressure | DECIMAL(6,3) | 壓力 (Decibar) |
| oxygen | DECIMAL(5,3) | 溶氧 (mg/L) |
| ph | DECIMAL(4,2) | 酸鹼值 |
| fluorescence | DECIMAL(6,3) | 螢光值 (ug/l) |
| turbidity | DECIMAL(6,3) | 濁度 (NTU) |
| salinity | DECIMAL(6,4) | 鹽度 (PSU) |

#### Trajectory (軌跡數據)
| 欄位 | 類型 | 說明 |
|------|------|------|
| station | ForeignKey | 關聯測站 |
| timestamp | DATETIME | 時間戳 |
| latitude | DECIMAL(9,6) | 緯度 |
| longitude | DECIMAL(9,6) | 經度 |
| speed | DECIMAL(5,2) | 速度 (m/s) |
| direction | DECIMAL(5,2) | 方向 (度) |

## 快速開始

### 1. 環境需求
- Python 3.10+
- Redis (用於 Celery 和 Channels)
- SQLite / PostgreSQL

### 2. 建立虛擬環境
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python -m venv venv
source venv/bin/activate
```

### 3. 安裝依賴
```bash
pip install -r requirements.txt
```

### 4. 環境變數設定
複製 `.env.example` 為 `.env` 並修改設定：
```env
# Django 基本設定
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Redis 連線
REDIS_URI=redis://127.0.0.1:6379/1

# Google Sheets (選填)
GOOGLE_CREDENTIALS_PATH=/path/to/credentials.json
GOOGLE_SHEET_ID=your-sheet-id

# Gemini AI (選填)
GEMINI_API_KEY=your-gemini-api-key
```

### 5. 資料庫初始化
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. 建立管理員帳號
```bash
python manage.py createsuperuser
```

### 7. 建立示範測站（選用）
```bash
python manage.py setup_demo_stations
```

### 8. 生成模擬數據（選用）
```bash
# 生成一次數據
python manage.py simulate_ocean_data

# 生成 10 輪數據
python manage.py simulate_ocean_data --count=10

# 持續生成（每分鐘一次）
python manage.py simulate_ocean_data --continuous
```

### 9. 啟動開發伺服器

#### 方法 1: 基本開發伺服器 (無 WebSocket)
```bash
python manage.py runserver
```

#### 方法 2: ASGI 伺服器 (支援 WebSocket)
```bash
# 使用 Daphne
daphne -b 127.0.0.1 -p 8000 config.asgi:application
```

### 10. 啟動 Celery (選用，用於定時任務)

#### Windows
```bash
# Celery Worker
celery -A config worker --pool=solo -l info

# Celery Beat (定時任務調度器)
celery -A config beat -l info
```

#### Mac/Linux
```bash
# Celery Worker
celery -A config worker -l info

# Celery Beat
celery -A config beat -l info
```

### 11. 啟動 Redis (必須，用於 Celery 和 WebSocket)
```bash
# Windows (需先安裝 Redis)
redis-server

# Mac
brew services start redis

# Linux
sudo service redis-server start
```

## 功能頁面

| 路徑 | 功能 | 說明 |
|------|------|------|
| `/` | 首頁 | 自動導向登入頁 |
| `/login/` | 登入頁 | 通用登入（支援 Google OAuth） |
| `/accounts/google/login/` | Google 登入 | OAuth 社交登入 |
| `/stations/` | 測站列表 | 瀏覽所有測站 |
| `/stations/<id>/` | 測站詳情 | 測站資料與即時圖表 |
| `/stations/<id>/trajectory/` | 軌跡圖 | 測站移動軌跡視覺化 |
| `/panel/` | 自訂後台 | 數據管理與分析面板 |
| `/admin/` | Django Admin | 系統管理（Celery Beat 排程） |

## 功能特色

### 核心功能
- ✅ **MTV 架構**: Django Model-Template-View 設計模式
- ✅ **自訂使用者系統**: Email/Username 雙重認證
- ✅ **Google OAuth**: 一鍵社交登入
- ✅ **一對多關係**: Station ↔ Reading / Trajectory

### 即時功能
- ✅ **WebSocket 即時推送**: 使用 Django Channels
- ✅ **即時圖表更新**: Chart.js 動態數據視覺化
- ✅ **即時軌跡追蹤**: 測站移動軌跡即時顯示

### 背景任務
- ✅ **Celery 定時任務**: 自動數據更新與分析
- ✅ **動態排程管理**: 透過 Django Admin 管理 Celery Beat
- ✅ **數據異常檢測**: 自動偵測異常數據並發送警報

### 數據處理
- ✅ **統計分析**: 自動計算平均值、最大最小值、標準差
- ✅ **數據模擬**: 生成符合真實分佈的模擬數據
- ✅ **Google Sheets 同步**: 自動同步數據到 Google Sheets
- ✅ **Gemini AI 分析**: AI 驅動的數據洞察與建議

### 開發工具
- ✅ **環境分離**: development/production 設定分離
- ✅ **靜態檔案處理**: WhiteNoise 無需額外配置
- ✅ **測試框架**: pytest + pytest-django
- ✅ **管理命令**: 自訂 Django management commands

## 技術棧

### 後端框架
- **Django 5.2**: Web 框架
- **Django Channels 4.3**: WebSocket 支援
- **Celery 5.6**: 分散式任務佇列
- **Redis 7.1**: 快取與訊息代理

### 認證與授權
- **django-allauth 65.3**: 社交登入整合
- **Google OAuth 2.0**: Google 帳號登入

### 前端
- **HTML5 + CSS3**: 響應式設計
- **JavaScript (ES6+)**: 互動邏輯
- **Chart.js 4.4**: 數據圖表
- **WebSocket API**: 即時通訊

### 第三方服務
- **Google Sheets API**: 數據同步
- **Gemini AI API**: AI 數據分析
- **WhiteNoise 6.8**: 靜態檔案服務

### 資料庫
- **SQLite**: 開發環境（預設）
- **PostgreSQL**: 生產環境（建議）

## 開發指令

### Django 管理
```bash
# 建立 migration
python manage.py makemigrations

# 執行 migration
python manage.py migrate

# 建立超級使用者
python manage.py createsuperuser

# 進入 Django Shell
python manage.py shell

# 收集靜態檔案
python manage.py collectstatic
```

### 自訂管理命令

#### 測站與數據管理
```bash
# 建立示範測站
python manage.py setup_demo_stations

# 生成模擬海洋數據
python manage.py simulate_ocean_data --count=10

# 生成軌跡數據
python manage.py generate_trajectory_data

# 重置軌跡數據
python manage.py reset_trajectory_data
```

#### 資料庫維護
```bash
# 修復資料庫欄位
python manage.py fix_db_columns
```

### 測試
```bash
# 執行所有測試
pytest

# 執行特定 app 測試
pytest station_data/tests/

# 測試涵蓋率報告
pytest --cov=. --cov-report=html
```

## 資料輸入方式

### 方法 1: 管理後台（推薦）
1. 訪問 `http://127.0.0.1:8000/admin/`
2. 登入管理員帳號
3. 新增測站和數據記錄

### 方法 2: 自訂後台
1. 訪問 `http://127.0.0.1:8000/panel/`
2. 使用自訂管理介面

### 方法 3: 管理命令
```bash
# 建立示範測站並生成數據
python manage.py setup_demo_stations
python manage.py simulate_ocean_data --count=10
```

### 方法 4: Django Shell
```bash
python manage.py shell
```
```python
from data_ingestion.models import Station, Reading
from datetime import datetime

# 建立測站
station = Station.objects.create(
    station_name='測站A',
    device_model='CR1000X',
    location='台北港',
    install_date='2024-01-01',
    latitude=25.1234,
    longitude=121.5678
)

# 建立數據
Reading.objects.create(
    station=station,
    timestamp=datetime.now(),
    temperature=28.5,
    ph=8.1,
    salinity=33.5
)
```

### 方法 5: Google Sheets 同步
配置好 Google Sheets API 後，Celery 會自動定時同步數據。

## 專案設定

### 環境變數

#### 必要設定
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
REDIS_URI=redis://127.0.0.1:6379/1
```

#### 選填設定（Google 相關）
```env
# Google Sheets
GOOGLE_CREDENTIALS_PATH=/path/to/credentials.json
GOOGLE_SHEET_ID=your-sheet-id

# Gemini AI
GEMINI_API_KEY=your-api-key
```

### 切換資料庫到 PostgreSQL

修改 `config/settings/base.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ocean_monitor',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Celery 定時任務

### 預設排程（在 base.py 中設定）

| 任務名稱 | 執行頻率 | 功能 |
|---------|---------|------|
| hourly-ocean-data-update | 每小時 | 更新海洋數據 |
| check-ocean-alerts | 每 6 小時 | 檢查數據異常 |
| daily-statistics | 每天 8:00 | 生成統計報告 |
| test-update-every-2-minutes | 每 2 分鐘 | 測試用（生產環境請移除） |

### 動態排程管理
訪問 Django Admin (`/admin/`) 的 Periodic Tasks 區塊，可以：
- 新增/編輯/刪除定時任務
- 調整執行時間
- 啟用/停用任務

## WebSocket 即時推送

### 連線端點
```javascript
// 連接測站即時數據
const socket = new WebSocket('ws://localhost:8000/ws/stations/<station_id>/');

// 接收數據
socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('新數據:', data);
};
```

### 推送內容
- 測站即時數據更新
- 數據異常警報
- 軌跡位置更新

## 部署

### 生產環境設定

1. **環境設定**
```bash
export DJANGO_SETTINGS_MODULE=config.settings.production
```

2. **安全設定**
```python
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']
SECRET_KEY = os.getenv('SECRET_KEY')  # 使用環境變數
```

3. **靜態檔案**
```bash
python manage.py collectstatic --noinput
```

4. **資料庫遷移**
```bash
python manage.py migrate
```

5. **啟動服務**
```bash
# ASGI 伺服器 (WebSocket 支援)
daphne -b 0.0.0.0 -p 8000 config.asgi:application

# Celery Worker
celery -A config worker -l info

# Celery Beat
celery -A config beat -l info
```

### Zeabur 部署
專案包含 `zbpack.json` 配置檔，支援一鍵部署到 Zeabur。

## 開發路線圖

- [ ] 數據匯出功能 (CSV, Excel)
- [ ] 多語系支援 (i18n)
- [ ] API 端點 (DRF)
- [ ] 更多 AI 分析功能
- [ ] 手機 App 整合
- [ ] 數據視覺化儀表板升級

## 授權

MIT License

## 聯絡方式

如有問題請聯繫開發者或提交 Issue。

---

**最後更新**: 2024-12-22
