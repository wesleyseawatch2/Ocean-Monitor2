# 快速修復指南

## 問題
```
django.db.utils.ProgrammingError: column station_data_report.station_id does not exist
```

## 原因
生產環境 PostgreSQL 資料庫缺少 `station_id` 欄位

## 解決方案（3 步驟）

### 方法 1：使用腳本（推薦）

```bash
# 1. 上傳並執行腳本
chmod +x deploy_migration.sh
./deploy_migration.sh

# 2. 重啟應用
sudo systemctl restart gunicorn
```

### 方法 2：手動執行

```bash
# 1. SSH 連線到生產伺服器
ssh user@your-production-server

# 2. 進入專案目錄
cd /path/to/ocean_monitor

# 3. 執行遷移
python manage.py migrate station_data

# 4. 重啟應用
sudo systemctl restart gunicorn
```

## 預期結果

遷移成功後會看到：
```
Operations to perform:
  Apply all migrations: station_data
Running migrations:
  Applying station_data.0002_report_station_alter_report_report_type... OK
```

## 驗證

訪問報告列表頁面應該正常顯示：
```
https://your-domain/stations/reports/
```

---

**需要幫助？** 查看完整文檔：DEPLOY_MIGRATION_GUIDE.md
