"""
快速示範 Google Sheets 讀取
"""

from utils.google_sheets import get_sheets_client
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

def main():
    print("=" * 60)
    print("Google Sheets 快速示範")
    print("=" * 60)
    print()

    # 取得客戶端
    client = get_sheets_client()
    sheet_id = os.getenv('GOOGLE_SHEET_ID')

    print(f"Sheet ID: {sheet_id}")
    print()

    # 讀取所有資料
    print("正在讀取資料...")
    all_data = client.read_all_data(sheet_id)

    print(f"[OK] 成功讀取! 共 {len(all_data)} 行資料")
    print()

    # 顯示前 10 行
    print("前 10 行資料:")
    print("-" * 60)
    for i, row in enumerate(all_data[:10], 1):
        print(f"第 {i:2d} 行: {row}")

    print("-" * 60)
    print()
    print(f"提示: 如果你的第一行是標題,可以使用 read_as_dict() 讀取為字典格式")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"錯誤: {str(e)}")
