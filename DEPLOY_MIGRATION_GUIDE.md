# 生產環境資料庫遷移指引

## 問題說明

錯誤訊息：
```
django.db.utils.ProgrammingError: column station_data_report.station_id does not exist
```

**原因**：生產環境的 PostgreSQL 資料庫尚未執行 `0002_report_station_alter_report_report_type` 遷移，因此缺少 `station_id` 欄位。

## 解決方案

### 在生產伺服器上執行以下命令：

```bash
# 1. 進入專案目錄
cd /path/to/ocean_monitor

# 2. 啟動虛擬環境（如果有使用）
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows

# 3. 檢查待執行的遷移
python manage.py showmigrations station_data

# 4. 執行遷移
python manage.py migrate station_data

# 5. 重啟 Django 應用
# 根據您的部署方式選擇：
sudo systemctl restart gunicorn  # systemd
# 或
supervisorctl restart ocean_monitor  # supervisor
# 或
kill -HUP <pid>  # 直接重啟進程
```

## 遷移內容

這個遷移會對 `station_data_report` 資料表進行以下變更：

1. **新增欄位** `station_id`（ForeignKey 到 data_ingestion_station 表）
   - 允許 NULL 值
   - 用於關聯測站特定的報告

2. **更新報告類型** 新增 `station_daily`（測站每日報告）選項

## PostgreSQL SQL 語句（參考）

如果您想手動檢查，遷移會執行類似以下的 SQL：

```sql
-- 添加 station_id 欄位
ALTER TABLE "station_data_report" 
ADD COLUMN "station_id" bigint NULL 
REFERENCES "data_ingestion_station" ("id") 
DEFERRABLE INITIALLY DEFERRED;

-- 創建索引
CREATE INDEX "station_data_report_station_id_xxx" 
ON "station_data_report" ("station_id");

-- 更新報告類型的 choices（在應用層面，不影響資料庫結構）
```

## 驗證遷移成功

執行遷移後，檢查資料表結構：

```bash
# 使用 Django shell
python manage.py shell

>>> from station_data.models import Report
>>> Report._meta.get_field('station')
<django.db.models.fields.related.ForeignKey: station>
```

或直接查詢 PostgreSQL：

```sql
\d station_data_report
-- 應該看到 station_id 欄位
```

## 注意事項

1. **資料備份**：在執行遷移前，請備份生產資料庫
   ```bash
   pg_dump ocean_monitor > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **停機時間**：這個遷移應該很快（添加可 NULL 的欄位），但建議在低流量時段執行

3. **回滾計畫**：如果遷移失敗，可以回滾：
   ```bash
   python manage.py migrate station_data 0001
   ```

## 相關文件

- 遷移文件：`station_data/migrations/0002_report_station_alter_report_report_type.py`
- 模型定義：`station_data/models.py`（第 36-43 行）

---

**創建日期**：2025-12-22  
**遷移版本**：0002_report_station_alter_report_report_type
