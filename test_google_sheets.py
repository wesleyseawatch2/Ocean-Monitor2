"""
Google Sheets 整合測試範例
示範如何使用 Google Sheets API 讀取和寫入資料
"""

from utils.google_sheets import get_sheets_client
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()


def test_read_sheet():
    """測試讀取 Google Sheet 資料"""
    print("=== 測試讀取 Google Sheet ===\n")

    # 取得 Google Sheets 客戶端
    client = get_sheets_client()

    # 從環境變數取得 Sheet ID
    sheet_id = os.getenv('GOOGLE_SHEET_ID')

    if not sheet_id:
        print("錯誤: 請在 .env 檔案中設定 GOOGLE_SHEET_ID")
        return

    try:
        # 方法 1: 讀取所有資料 (二維陣列)
        print("1. 讀取所有資料:")
        all_data = client.read_all_data(sheet_id)
        for i, row in enumerate(all_data[:5], 1):  # 只顯示前 5 行
            print(f"   第 {i} 行: {row}")
        print()

        # 方法 2: 讀取為字典列表 (第一行為欄位名稱)
        print("2. 讀取為字典格式:")
        dict_data = client.read_as_dict(sheet_id)
        for i, record in enumerate(dict_data[:3], 1):  # 只顯示前 3 筆
            print(f"   記錄 {i}: {record}")
        print()

        # 方法 3: 讀取特定範圍
        print("3. 讀取特定範圍 (A1:C5):")
        range_data = client.read_range(sheet_id, 'A1:C5')
        for row in range_data:
            print(f"   {row}")
        print()

    except Exception as e:
        print(f"讀取失敗: {str(e)}")


def test_write_sheet():
    """測試寫入資料到 Google Sheet"""
    print("\n=== 測試寫入 Google Sheet ===\n")

    client = get_sheets_client()
    sheet_id = os.getenv('GOOGLE_SHEET_ID')

    if not sheet_id:
        print("錯誤: 請在 .env 檔案中設定 GOOGLE_SHEET_ID")
        return

    try:
        # 準備要寫入的資料
        data = [
            ['測站名稱', '溫度', '濕度', '時間'],
            ['台北站', '25.5', '70', '2024-12-06 10:00'],
            ['高雄站', '28.3', '65', '2024-12-06 10:00'],
            ['台中站', '26.8', '68', '2024-12-06 10:00'],
        ]

        # 寫入資料 (從 A1 開始)
        print("寫入測試資料到工作表...")
        client.write_data(sheet_id, data, start_cell='A1')
        print("✓ 寫入成功!\n")

        # 新增單行資料
        new_row = [['花蓮站', '24.2', '75', '2024-12-06 10:00']]
        print("新增一筆資料...")
        client.append_rows(sheet_id, new_row)
        print("✓ 新增成功!")

    except Exception as e:
        print(f"寫入失敗: {str(e)}")


def example_ocean_data_import():
    """範例: 從 Google Sheets 匯入海洋監測資料"""
    print("\n=== 範例: 匯入海洋監測資料 ===\n")

    client = get_sheets_client()
    sheet_id = os.getenv('GOOGLE_SHEET_ID')

    if not sheet_id:
        print("錯誤: 請在 .env 檔案中設定 GOOGLE_SHEET_ID")
        return

    try:
        # 讀取資料為字典格式
        records = client.read_as_dict(sheet_id)

        print(f"共讀取 {len(records)} 筆資料\n")

        # 處理每筆資料
        for i, record in enumerate(records[:5], 1):
            print(f"資料 {i}:")
            print(f"  測站: {record.get('測站名稱', 'N/A')}")
            print(f"  溫度: {record.get('溫度', 'N/A')}°C")
            print(f"  濕度: {record.get('濕度', 'N/A')}%")
            print(f"  時間: {record.get('時間', 'N/A')}")
            print()

            # 這裡可以將資料儲存到 Django 模型
            # 例如:
            # Reading.objects.create(
            #     station=record.get('測站名稱'),
            #     temperature=record.get('溫度'),
            #     humidity=record.get('濕度'),
            #     timestamp=record.get('時間')
            # )

    except Exception as e:
        print(f"匯入失敗: {str(e)}")


if __name__ == '__main__':
    print("Google Sheets API 測試程式\n")
    print("=" * 50)

    # 檢查環境變數
    if not os.getenv('GOOGLE_CREDENTIALS_JSON') and not os.getenv('GOOGLE_CREDENTIALS_PATH'):
        print("\n⚠️  警告: 尚未設定 Google API 憑證!")
        print("\n請先完成以下步驟:")
        print("1. 到 Google Cloud Console 建立 Service Account")
        print("2. 下載 JSON 憑證檔案")
        print("3. 在 .env 設定 GOOGLE_CREDENTIALS_JSON 或 GOOGLE_CREDENTIALS_PATH")
        print("4. 設定 GOOGLE_SHEET_ID (你的 Google Sheet ID)")
        print("\n詳細說明請參考 GOOGLE_SHEETS_GUIDE.md")
        print("=" * 50)
    else:
        # 執行測試
        try:
            test_read_sheet()
            # test_write_sheet()  # 取消註解以測試寫入功能
            # example_ocean_data_import()  # 取消註解以測試資料匯入
        except Exception as e:
            print(f"\n❌ 測試失敗: {str(e)}")
