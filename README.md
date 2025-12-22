# Ocean Monitor Web

基於 Django MTV 架構的海洋數據監測與可視化系統。

## 專案架構
```
ocean_monitor/
├── config/                    # Django 專案設定
│   ├── settings/
│   │   ├── base.py           # 共用設定
│   │   └── development.py    # 開發環境設定
│   ├── urls.py               # 主 URL 路由
│   ├── wsgi.py               # WSGI 配置
│   └── asgi.py               # ASGI 配置
├── data_ingestion/           # 數據接收 App
│   ├── models.py             # Station 和 Reading Models
│   └── admin.py              # 管理後台設定
├── station_data/             # MTV 主流程 App
│   ├── views.py              # 視圖邏輯
│   └── urls.py               # App URL 路由
├── analysis_tools/           # 分析工具 App
│   ├── calculations.py       # 統計分析函數
│   └── chart_helpers.py      # 圖表數據轉換
├── templates/                # HTML 模板
│   ├── base.html
│   └── station_data/
├── manage.py                 # Django 管理腳本
└── create_sample_data.py     # 範例資料生成
```

## 資料庫架構

### Station（測站）- 一對多的「一」
| 欄位 | 類型 | 說明 |
|------|------|------|
| station_name | VARCHAR(100) | 測站名稱 |
| device_model | VARCHAR(50) | 設備型號 |
| location | VARCHAR(100) | 裝設地點 |
| install_date | DATE | 裝設日期 |

### Reading（數據記錄）- 一對多的「多」
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


## 快速開始

### 1. 建立專案結構
```bash
python create_structure.py
cd ocean_monitor
```

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
pip install django
```

### 4. 資料庫初始化
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. 建立管理員帳號
```bash
python manage.py createsuperuser
```

### 6. 建立範例資料（選用）
```bash
python create_sample_data.py
```

### 7. 啟動開發伺服器
```bash
python manage.py runserver
```

## 功能頁面

| 路徑 | 功能 |
|------|------|
| `/` | 測站列表 |
| `/stations/<id>/` | 測站詳細資料與圖表 |
| `/readings/` | 所有數據記錄 |
| `/admin/` | 管理後台 |

## 功能特色

- ✅ **MTV 架構**：遵循 Django Model-Template-View 設計模式
- ✅ **一對多關係**：Station ↔ Reading
- ✅ **統計分析**：自動計算平均值、最大最小值
- ✅ **數據可視化**：使用 Chart.js 繪製趨勢圖
- ✅ **響應式設計**：支援各種螢幕尺寸
- ✅ **環境分離**：development/production 設定分離
- ✅ **管理後台**：Django Admin 快速管理資料

## 技術棧

- **後端**：Django 4.2+
- **前端**：HTML5, CSS3, JavaScript
- **圖表**：Chart.js 4.4
- **資料庫**：SQLite（可替換為 PostgreSQL/MySQL）

## 開發指令
```bash
# 建立新的 migration
python manage.py makemigrations

# 執行 migration
python manage.py migrate

# 啟動開發伺服器
python manage.py runserver

# 進入 Django Shell
python manage.py shell

# 建立超級使用者
python manage.py createsuperuser

# 收集靜態檔案
python manage.py collectstatic
```

## 資料輸入方式

### 方法 1：管理後台（推薦）
1. 訪問 http://127.0.0.1:8000/admin/
2. 登入管理員帳號
3. 新增測站和數據記錄

### 方法 2：Django Shell
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
    install_date='2024-01-01'
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

### 方法 3：範例資料腳本
```bash
python create_sample_data.py
```

## 專案設定

### 環境變數
複製 `.env.example` 為 `.env` 並修改設定：
```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 切換資料庫（PostgreSQL）
修改 `config/settings/base.py`：
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

## 部署

### 生產環境設定
1. 修改 `config/settings/production.py`
2. 設定 `DEBUG=False`
3. 配置 `ALLOWED_HOSTS`
4. 使用環境變數管理 `SECRET_KEY`
5. 配置靜態檔案服務

## 授權

MIT License

## 聯絡方式

如有問題請聯繫開發者。