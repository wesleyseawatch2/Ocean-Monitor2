# Ocean Monitor 測試指南

## 測試架構說明

本專案使用 **pytest** 作為測試框架，搭配 **pytest-django** 進行 Django 整合測試。

## 測試檔案結構

```
ocean_monitor/
├── conftest.py                           # 全專案共用的 fixtures
├── pytest.ini                            # pytest 設定檔
│
├── apps/core/
│   ├── accounts/tests/
│   │   ├── __init__.py
│   │   └── test_models.py                # User 模型測試
│   └── tests/
│       ├── __init__.py
│       └── test_views.py                 # 登入功能測試
│
├── data_ingestion/tests/
│   ├── __init__.py
│   └── test_models.py                    # Station & Reading 模型測試
│
├── analysis_tools/tests/
│   ├── __init__.py
│   ├── test_calculations.py              # 統計計算函數測試
│   └── test_chart_helpers.py             # 圖表數據轉換測試
│
├── station_data/tests/
│   ├── __init__.py
│   └── test_views.py                     # 測站資料頁面測試
│
└── admin_panel/tests/
    ├── __init__.py
    └── test_views.py                     # 後台管理功能測試
```

## 快速開始

### 1. 安裝測試依賴

```bash
pip install pytest pytest-django pytest-cov
```

### 2. 執行所有測試

```bash
# 基本執行
pytest

# 顯示詳細輸出
pytest -v

# 顯示 print 輸出（除錯用）
pytest -s

# 在第一個錯誤時停止
pytest -x

# 執行特定測試檔案
pytest apps/core/accounts/tests/test_models.py

# 執行特定測試函數
pytest apps/core/accounts/tests/test_models.py::test_user_creation
```

### 3. 測試覆蓋率報告

```bash
# 產生覆蓋率報告
pytest --cov=apps --cov=data_ingestion --cov=analysis_tools --cov=station_data --cov=admin_panel

# 顯示哪些行沒被覆蓋
pytest --cov=apps --cov-report=term-missing

# 產生 HTML 報告
pytest --cov=apps --cov-report=html

# 開啟 HTML 報告（會自動在瀏覽器開啟）
start htmlcov/index.html
```

## 測試說明

### 📁 User Model 測試 (apps/core/accounts/tests/test_models.py)

測試內容：
- ✅ 使用者建立（一般使用者、管理員、超級使用者）
- ✅ 自訂欄位（電話、頭像、個人簡介）
- ✅ 使用者權限
- ✅ 密碼驗證
- ✅ 查詢功能

### 📁 Station & Reading Model 測試 (data_ingestion/tests/test_models.py)

測試內容：
- ✅ 測站建立與查詢
- ✅ 數據記錄建立
- ✅ 外鍵關係 (Station ↔ Reading)
- ✅ 級聯刪除 (cascade delete)
- ✅ NULL 值處理
- ✅ Decimal 精度測試
- ✅ 時間範圍查詢

### 📁 計算函數測試 (analysis_tools/tests/test_calculations.py)

測試內容：
- ✅ `calculate_average()` - 平均值計算
- ✅ `calculate_min_max()` - 最小最大值
- ✅ `calculate_statistics()` - 統計資料（整合測試）
- ✅ 空陣列處理
- ✅ NULL 值處理
- ✅ Decimal 類型支援

### 📁 圖表輔助函數測試 (analysis_tools/tests/test_chart_helpers.py)

測試內容：
- ✅ `prepare_chart_data()` - 圖表數據轉換
- ✅ 時間標籤格式 (MM/DD HH:MM)
- ✅ Decimal 轉 float
- ✅ 數據反轉（舊到新）
- ✅ NULL 值處理

### 📁 登入功能測試 (apps/core/tests/test_views.py)

測試內容：
- ✅ 登入頁面顯示
- ✅ 正確帳號密碼登入
- ✅ 錯誤密碼處理
- ✅ 使用者重定向（一般使用者 → /stations/）
- ✅ 管理員重定向（管理員 → /panel/）
- ✅ 已登入使用者自動跳轉

### 📁 測站資料頁面測試 (station_data/tests/test_views.py)

測試內容：
- ✅ 測站列表頁面
- ✅ 測站詳情頁面
- ✅ 統計資料計算
- ✅ 圖表數據 JSON 格式
- ✅ 數據記錄列表
- ✅ 404 錯誤處理

### 📁 後台管理功能測試 (admin_panel/tests/test_views.py)

測試內容：
- ✅ 權限控制（`@staff_required`）
- ✅ 儀表板統計資料
- ✅ 測站 CRUD 操作（新增、編輯、刪除）
- ✅ 數據記錄列表
- ✅ 使用者列表
- ✅ 定時任務管理
- ✅ 登出功能

## 共用 Fixtures (conftest.py)

專案提供了以下共用 fixtures，可在任何測試中直接使用：

### 使用者相關
- `user` - 一般測試使用者
- `staff_user` - 管理員使用者
- `authenticated_client` - 已登入的一般使用者 client
- `staff_authenticated_client` - 已登入的管理員 client

### 測站相關
- `station` - 單一測試測站
- `station_b` - 第二個測試測站
- `multiple_stations` - 3 個測試測站

### 數據記錄相關
- `reading` - 單筆測試數據
- `multiple_readings` - 10 筆時間序列數據
- `readings_with_null_values` - 包含 NULL 值的測試數據

### 使用範例

```python
def test_example(station, multiple_readings):
    """使用共用 fixtures 的測試範例"""
    assert station.readings.count() == 10
    assert multiple_readings[0].temperature is not None
```

## 測試最佳實踐

### ✅ 好的做法

1. **測試名稱要清楚描述測試內容**
   ```python
   # Good
   def test_user_login_with_valid_credentials():
       ...

   # Bad
   def test1():
       ...
   ```

2. **每個測試只測試一件事**
   ```python
   # Good - 分開測試
   def test_station_creation():
       ...

   def test_station_str_method():
       ...

   # Bad - 測試太多東西
   def test_station():
       # 測試建立
       # 測試 __str__
       # 測試查詢
       # ...
   ```

3. **使用 fixtures 準備測試資料**
   ```python
   # Good
   def test_reading_creation(reading):
       assert reading.temperature == Decimal('25.5')

   # Bad - 在測試中重複建立資料
   def test_reading_creation():
       station = Station.objects.create(...)
       reading = Reading.objects.create(...)
       ...
   ```

### ❌ 避免的做法

1. **測試之間有相依性**
2. **測試依賴外部服務**（除非是整合測試）
3. **使用模糊的測試名稱**
4. **不清理測試資料**（pytest-django 會自動處理）

## 常見問題

### Q1: 測試資料庫錯誤

```
django.db.utils.OperationalError: no such table
```

**解決方案：**
```bash
python manage.py makemigrations
python manage.py migrate
```

### Q2: 找不到 URL

```
django.urls.exceptions.NoReverseMatch
```

**解決方案：**
確認 `urls.py` 中有設定 `app_name` 和正確的 `name` 參數。

### Q3: Fixture 找不到

```
fixture 'station' not found
```

**解決方案：**
確認 `conftest.py` 檔案位置正確，且 fixture 名稱拼寫正確。

## 進階技巧

### 平行執行測試（加速）

```bash
# 安裝 pytest-xdist
pip install pytest-xdist

# 自動使用所有 CPU 核心
pytest -n auto
```

### 只執行失敗的測試

```bash
# 第一次執行
pytest

# 只執行上次失敗的測試
pytest --lf
```

### 測試特定標記

```python
# 在測試上加上標記
@pytest.mark.slow
def test_slow_operation():
    ...

# 執行時跳過慢速測試
pytest -m "not slow"
```

## 目標覆蓋率

建議目標：
- Model 測試覆蓋率：**90%+**
- View 測試覆蓋率：**80%+**
- 工具函數覆蓋率：**95%+**

⚠️ **注意**：覆蓋率 100% 不代表沒有 bug！重點是測試有沒有正確驗證邏輯。

## 持續整合 (CI/CD)

建議在 GitHub Actions 或其他 CI 工具中自動執行測試：

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.10
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-django pytest-cov
      - name: Run tests
        run: pytest --cov
```

## 總結

本專案已建立完整的測試架構，涵蓋：
- ✅ 8 個測試檔案
- ✅ 100+ 個測試案例
- ✅ Model、View、工具函數全面覆蓋
- ✅ 權限控制測試
- ✅ 錯誤處理測試

執行測試來確保程式碼品質！ 🚀
