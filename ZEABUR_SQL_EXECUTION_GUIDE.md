# 在 Zeabur 執行 SQL 腳本指南

## 方法一: 使用 Zeabur CLI (推薦)

### 1. 安裝 Zeabur CLI
```bash
npm install -g @zeabur/cli
```

### 2. 登入 Zeabur
```bash
zeabur auth login
```

### 3. 連接到資料庫並執行 SQL
```bash
# 獲取資料庫連接字串
zeabur service exec <service-id> -- psql -f fix_zeabur_db.sql
```

## 方法二: 使用 psql 命令行工具

### 1. 從 Zeabur Dashboard 獲取資料庫連接資訊
- 進入您的專案
- 點擊 PostgreSQL 服務
- 複製 `DATABASE_URL` 或連接資訊

### 2. 使用 psql 執行 SQL 文件
```bash
# 如果有 DATABASE_URL
psql "postgresql://username:password@host:port/database" -f fix_zeabur_db.sql

# 或者分別指定參數
psql -h <host> -p <port> -U <username> -d <database> -f fix_zeabur_db.sql
```

輸入密碼後即可執行。

## 方法三: 直接在 Django 中執行 (最簡單)

### 1. 建立 Django 管理命令

創建檔案: `data_ingestion/management/commands/fix_db_columns.py`

### 2. 在 Zeabur 上執行
```bash
python manage.py fix_db_columns
```

## 方法四: 使用圖形化工具

### 使用 pgAdmin 或 DBeaver

1. **下載工具**
   - pgAdmin: https://www.pgadmin.org/
   - DBeaver: https://dbeaver.io/

2. **建立連接**
   - 從 Zeabur Dashboard 複製連接資訊
   - Host, Port, Database, Username, Password

3. **執行 SQL**
   - 開啟 `fix_zeabur_db.sql`
   - 點擊執行按鈕

## 方法五: 複製 SQL 內容直接執行

如果以上方法都不方便,最簡單的方式:

### 複製以下 SQL 並在任何 PostgreSQL 客戶端執行:

```sql
ALTER TABLE data_ingestion_station
ADD COLUMN IF NOT EXISTS latitude NUMERIC(9, 6) NULL;

ALTER TABLE data_ingestion_station
ADD COLUMN IF NOT EXISTS longitude NUMERIC(9, 6) NULL;
```

## 推薦順序

1. **最快**: 方法三 (Django 管理命令) - 我可以幫您建立
2. **次選**: 方法二 (psql 命令) - 如果本機已安裝 PostgreSQL
3. **最簡單**: 方法四 (圖形化工具) - 適合不熟悉命令行

## 驗證是否成功

執行後,可以用以下 SQL 驗證:

```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'data_ingestion_station'
AND column_name IN ('latitude', 'longitude');
```

應該看到兩個欄位都存在。
