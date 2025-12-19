# Zeabur 部署 - 資料庫欄位缺失修復指南

## 問題描述
部署到 Zeabur 後出現錯誤:
```
django.db.utils.ProgrammingError: column data_ingestion_station.latitude does not exist
```

## 原因
遷移記錄顯示 `0002_station_latitude_station_longitude` 已應用,但資料庫表實際上沒有這些欄位。

## 解決方案

### 方法一:使用 SQL 腳本(推薦)

1. **連接到 Zeabur PostgreSQL 資料庫**
   - 在 Zeabur Dashboard 中找到 PostgreSQL 服務
   - 使用提供的連接資訊連接(可使用 pgAdmin, DBeaver, 或命令行)

2. **執行 SQL 腳本**
   ```bash
   # 使用 psql 命令行工具
   psql <ZEABUR_DATABASE_URL> -f fix_zeabur_db.sql
   ```

   或者在 SQL 客戶端中直接執行 `fix_zeabur_db.sql` 的內容

3. **驗證欄位已新增**
   ```sql
   SELECT column_name, data_type
   FROM information_schema.columns
   WHERE table_name = 'data_ingestion_station'
   AND column_name IN ('latitude', 'longitude');
   ```

4. **重啟 Zeabur 服務**
   - 在 Zeabur Dashboard 中重新部署應用

### 方法二:重置遷移(如果資料不重要)

如果可以清空資料庫重來:

1. **在 Zeabur 中執行**
   ```bash
   # 刪除所有表
   python manage.py flush --no-input

   # 重新執行所有遷移
   python manage.py migrate
   ```

2. **重新部署**

### 方法三:假遷移後重新應用

如果其他方法不適用:

1. **回退遷移記錄**
   ```bash
   python manage.py migrate data_ingestion 0001 --fake
   ```

2. **重新應用遷移**
   ```bash
   python manage.py migrate data_ingestion
   ```

## 預防措施

### 確保遷移在部署時正確執行

在 Zeabur 的部署設置中,確保 `start` 命令包含遷移:

```bash
python manage.py migrate --no-input && daphne -b 0.0.0.0 -p $PORT ocean_monitor.asgi:application
```

### 檢查環境變數

確保 Zeabur 上設置了正確的資料庫環境變數:
- `DATABASE_URL` 或
- `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`

## 驗證修復

修復後,訪問以下 URL 確認正常:
```
https://your-app.zeabur.app/stations/1/?time_range=7d
```

應該不再出現 `latitude does not exist` 錯誤。

## 相關檔案
- 遷移檔案: `data_ingestion/migrations/0002_station_latitude_station_longitude.py`
- 模型定義: `data_ingestion/models.py` (第 11-12 行)
- SQL 修復腳本: `fix_zeabur_db.sql`
