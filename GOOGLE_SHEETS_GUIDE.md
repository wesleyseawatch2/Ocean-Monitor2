# Google Sheets API 整合指南

本專案已整合 Google Sheets API,可以讀取和寫入 Google 試算表資料。

## 📋 目錄

1. [設定步驟](#設定步驟)
2. [使用方式](#使用方式)
3. [常見功能](#常見功能)
4. [在 Django 中使用](#在-django-中使用)
5. [部署到 Zeabur](#部署到-zeabur)

---

## 🔧 設定步驟

### 步驟 1: 建立 Google Cloud Project

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立新專案或選擇現有專案
3. 點擊左上角選單 → 「API 和服務」→ 「資訊主頁」

### 步驟 2: 啟用 Google Sheets API

1. 在 API 資訊主頁,點擊「+ 啟用 API 和服務」
2. 搜尋「Google Sheets API」
3. 點擊啟用
4. 同樣方式啟用「Google Drive API」

### 步驟 3: 建立 Service Account

1. 點擊左側選單「憑證」
2. 點擊「+ 建立憑證」→ 選擇「服務帳戶」
3. 填寫服務帳戶名稱 (例如: `ocean-monitor-sheets`)
4. 點擊「建立並繼續」
5. 角色選擇「編輯者」或「擁有者」
6. 點擊「完成」

### 步驟 4: 建立 JSON 金鑰

1. 在憑證頁面,找到剛建立的服務帳戶
2. 點擊服務帳戶進入詳細資訊
3. 切換到「金鑰」分頁
4. 點擊「新增金鑰」→ 選擇「JSON」
5. 系統會自動下載 JSON 檔案 (妥善保管此檔案!)

### 步驟 5: 設定環境變數

**方法 1: 使用 JSON 檔案路徑** (本地開發推薦)

在 `.env` 檔案中設定:
```env
GOOGLE_CREDENTIALS_PATH=path/to/your/credentials.json
GOOGLE_SHEET_ID=your_google_sheet_id
```

**方法 2: 直接貼上 JSON 內容** (部署到雲端推薦)

在 `.env` 檔案中設定:
```env
GOOGLE_CREDENTIALS_JSON={"type":"service_account","project_id":"your-project",...}
GOOGLE_SHEET_ID=your_google_sheet_id
```

### 步驟 6: 分享 Google Sheet 給 Service Account

1. 開啟你要存取的 Google Sheet
2. 點擊右上角「共用」按鈕
3. 將 Service Account 的電子郵件地址加入共用對象
   - 電子郵件格式: `your-service-account@your-project.iam.gserviceaccount.com`
   - 可以在下載的 JSON 檔案中找到 `client_email` 欄位
4. 給予「編輯者」權限 (如果需要寫入)

### 步驟 7: 取得 Google Sheet ID

從 Google Sheet 網址取得 Sheet ID:
```
https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit
                                       ^^^^^^^^^^^^^^
                                       這就是你的 Sheet ID
```

---

## 💻 使用方式

### 基本讀取範例

```python
from utils.google_sheets import get_sheets_client

# 取得客戶端
client = get_sheets_client()

# 讀取所有資料
sheet_id = "your_sheet_id_here"
data = client.read_all_data(sheet_id)
print(data)
```

### 讀取為字典格式

```python
# 第一行會被當作欄位名稱
records = client.read_as_dict(sheet_id)

for record in records:
    print(record['欄位名稱'])
```

### 寫入資料

```python
# 準備資料
data = [
    ['欄位1', '欄位2', '欄位3'],
    ['值1', '值2', '值3'],
    ['值4', '值5', '值6'],
]

# 寫入到 Sheet
client.write_data(sheet_id, data, start_cell='A1')
```

### 新增資料到末尾

```python
# 新增一行或多行
new_rows = [
    ['新值1', '新值2', '新值3'],
    ['新值4', '新值5', '新值6'],
]

client.append_rows(sheet_id, new_rows)
```

---

## 🎯 常見功能

### 讀取特定範圍

```python
# 讀取 A1:C10 範圍的資料
data = client.read_range(sheet_id, 'A1:C10')
```

### 指定工作表名稱

```python
# 讀取名為 "2024資料" 的工作表
data = client.read_all_data(sheet_id, worksheet_name='2024資料')
```

### 建立新工作表

```python
# 在現有 Google Sheet 中建立新工作表
new_sheet = client.create_worksheet(
    sheet_id,
    title='新工作表',
    rows=100,
    cols=20
)
```

### 清空工作表

```python
# 清空所有資料
client.clear_sheet(sheet_id)
```

---

## 🐍 在 Django 中使用

### 範例 1: 從 Google Sheets 匯入海洋資料

```python
# station_data/management/commands/import_from_sheets.py

from django.core.management.base import BaseCommand
from utils.google_sheets import get_sheets_client
from station_data.models import Station, Reading
from datetime import datetime
import os

class Command(BaseCommand):
    help = '從 Google Sheets 匯入海洋監測資料'

    def handle(self, *args, **options):
        client = get_sheets_client()
        sheet_id = os.getenv('GOOGLE_SHEET_ID')

        # 讀取資料
        records = client.read_as_dict(sheet_id)

        for record in records:
            # 取得或建立測站
            station, _ = Station.objects.get_or_create(
                name=record['測站名稱']
            )

            # 建立監測資料
            Reading.objects.create(
                station=station,
                water_temperature=float(record['水溫']),
                wave_height=float(record['波高']),
                timestamp=datetime.fromisoformat(record['時間'])
            )

        self.stdout.write(
            self.style.SUCCESS(f'成功匯入 {len(records)} 筆資料')
        )
```

執行指令:
```bash
python manage.py import_from_sheets
```

### 範例 2: 在 View 中讀取 Google Sheets

```python
# station_data/views.py

from django.shortcuts import render
from utils.google_sheets import get_sheets_client
import os

def google_sheets_data(request):
    client = get_sheets_client()
    sheet_id = os.getenv('GOOGLE_SHEET_ID')

    try:
        # 讀取資料
        data = client.read_as_dict(sheet_id)

        context = {
            'sheet_data': data,
            'total_records': len(data)
        }
        return render(request, 'sheets_data.html', context)

    except Exception as e:
        context = {'error': str(e)}
        return render(request, 'sheets_data.html', context)
```

### 範例 3: 建立 Celery 定時任務

```python
# station_data/tasks.py

from celery import shared_task
from utils.google_sheets import get_sheets_client
from station_data.models import Reading
import os

@shared_task
def sync_data_from_google_sheets():
    """每小時從 Google Sheets 同步資料"""
    client = get_sheets_client()
    sheet_id = os.getenv('GOOGLE_SHEET_ID')

    records = client.read_as_dict(sheet_id)

    for record in records:
        # 處理並儲存資料
        # ...
        pass

    return f'已同步 {len(records)} 筆資料'
```

在 `config/settings/base.py` 設定排程:
```python
CELERY_BEAT_SCHEDULE = {
    'sync-google-sheets-hourly': {
        'task': 'station_data.tasks.sync_data_from_google_sheets',
        'schedule': crontab(minute=0),  # 每小時執行
    },
}
```

---

## 🚀 部署到 Zeabur

### 設定環境變數

在 Zeabur 專案設定中,新增以下環境變數:

1. `GOOGLE_CREDENTIALS_JSON`: 將整個 JSON 憑證內容貼上
2. `GOOGLE_SHEET_ID`: 你的 Google Sheet ID

### 提示

- JSON 憑證要壓縮成單行 (移除換行符號)
- 可以使用線上工具如 [JSON Formatter](https://jsonformatter.org/) 來壓縮 JSON
- 確保憑證內容包含雙引號

---

## 🧪 測試

執行測試程式:

```bash
python test_google_sheets.py
```

這會測試:
- ✅ Google API 連線
- ✅ 讀取 Sheet 資料
- ✅ 寫入資料 (如果取消註解)
- ✅ 資料格式轉換

---

## 📚 參考資源

- [Google Sheets API 文件](https://developers.google.com/sheets/api)
- [gspread 套件文件](https://docs.gspread.org/)
- [Google Cloud Console](https://console.cloud.google.com/)

---

## ⚠️ 注意事項

1. **安全性**: 不要將 Service Account JSON 憑證提交到 Git
2. **配額限制**: Google Sheets API 有使用配額限制,請參考官方文件
3. **權限**: 確保 Service Account 有存取目標 Sheet 的權限
4. **錯誤處理**: 建議在程式中加入適當的錯誤處理機制

---

## 🆘 常見問題

### Q: 出現 "Permission denied" 錯誤?
A: 確認已將 Service Account 的電子郵件加入 Google Sheet 的共用對象

### Q: 出現 "API has not been used" 錯誤?
A: 確認已在 Google Cloud Console 啟用 Google Sheets API 和 Google Drive API

### Q: 如何找到 Service Account 的電子郵件?
A: 在下載的 JSON 憑證檔案中找到 `client_email` 欄位

### Q: 可以同時存取多個 Google Sheets 嗎?
A: 可以!只要將 Service Account 加入所有需要存取的 Sheets 即可

---

如有任何問題,歡迎查看測試檔案 `test_google_sheets.py` 或參考 `utils/google_sheets.py` 原始碼。
