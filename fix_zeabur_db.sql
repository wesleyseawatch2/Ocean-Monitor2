-- 修復 Zeabur 資料庫缺少 latitude 和 longitude 欄位的問題
-- 在 Zeabur PostgreSQL 環境中執行此 SQL

-- 檢查欄位是否存在,如果不存在則新增
DO $$
BEGIN
    -- 新增 latitude 欄位
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'data_ingestion_station'
        AND column_name = 'latitude'
    ) THEN
        ALTER TABLE data_ingestion_station
        ADD COLUMN latitude NUMERIC(9, 6) NULL;
        RAISE NOTICE 'Added latitude column';
    ELSE
        RAISE NOTICE 'latitude column already exists';
    END IF;

    -- 新增 longitude 欄位
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'data_ingestion_station'
        AND column_name = 'longitude'
    ) THEN
        ALTER TABLE data_ingestion_station
        ADD COLUMN longitude NUMERIC(9, 6) NULL;
        RAISE NOTICE 'Added longitude column';
    ELSE
        RAISE NOTICE 'longitude column already exists';
    END IF;
END $$;
