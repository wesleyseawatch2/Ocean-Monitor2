"""
Google Sheets 整合模組
提供讀取和寫入 Google Sheets 的功能
"""

import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Optional
import os
import json


class GoogleSheetsClient:
    """Google Sheets 客戶端類別"""

    # Google Sheets API 所需的權限範圍
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    def __init__(self, credentials_path: Optional[str] = None):
        """
        初始化 Google Sheets 客戶端

        Args:
            credentials_path: Google Service Account JSON 憑證檔案路徑
                            如果不提供，會從環境變數 GOOGLE_CREDENTIALS_JSON 讀取
        """
        self.credentials_path = credentials_path
        self.client = None
        self._authenticate()

    def _authenticate(self):
        """驗證並建立 Google Sheets 客戶端"""
        try:
            creds = None

            # 優先使用傳入的 credentials_path
            if self.credentials_path and os.path.exists(self.credentials_path):
                # 從檔案讀取憑證
                creds = Credentials.from_service_account_file(
                    self.credentials_path,
                    scopes=self.SCOPES
                )
            else:
                # 嘗試從環境變數 GOOGLE_CREDENTIALS_PATH 讀取檔案路徑
                env_credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH')
                if env_credentials_path and os.path.exists(env_credentials_path):
                    creds = Credentials.from_service_account_file(
                        env_credentials_path,
                        scopes=self.SCOPES
                    )
                else:
                    # 從環境變數讀取憑證 JSON 內容
                    credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
                    if credentials_json:
                        credentials_dict = json.loads(credentials_json)
                        creds = Credentials.from_service_account_info(
                            credentials_dict,
                            scopes=self.SCOPES
                        )

            if not creds:
                raise ValueError(
                    "請提供 credentials_path 參數,或設定 GOOGLE_CREDENTIALS_PATH 或 GOOGLE_CREDENTIALS_JSON 環境變數"
                )

            self.client = gspread.authorize(creds)

        except Exception as e:
            raise Exception(f"Google Sheets 驗證失敗: {str(e)}")

    def open_sheet(self, spreadsheet_id: str, worksheet_name: str = None):
        """
        開啟指定的 Google Sheet

        Args:
            spreadsheet_id: Google Sheet 的 ID (從網址中取得)
            worksheet_name: 工作表名稱 (如果不提供，使用第一個工作表)

        Returns:
            worksheet: gspread Worksheet 物件
        """
        try:
            spreadsheet = self.client.open_by_key(spreadsheet_id)

            if worksheet_name:
                worksheet = spreadsheet.worksheet(worksheet_name)
            else:
                worksheet = spreadsheet.sheet1  # 預設使用第一個工作表

            return worksheet

        except Exception as e:
            raise Exception(f"開啟 Google Sheet 失敗: {str(e)}")

    def read_all_data(self, spreadsheet_id: str, worksheet_name: str = None) -> List[List]:
        """
        讀取整個工作表的所有資料

        Args:
            spreadsheet_id: Google Sheet 的 ID
            worksheet_name: 工作表名稱

        Returns:
            List[List]: 二維列表,包含所有儲存格的值
        """
        worksheet = self.open_sheet(spreadsheet_id, worksheet_name)
        return worksheet.get_all_values()

    def read_as_dict(self, spreadsheet_id: str, worksheet_name: str = None) -> List[Dict]:
        """
        讀取工作表資料並轉換為字典列表 (第一行為欄位名稱)

        Args:
            spreadsheet_id: Google Sheet 的 ID
            worksheet_name: 工作表名稱

        Returns:
            List[Dict]: 字典列表,每個字典代表一行資料
        """
        worksheet = self.open_sheet(spreadsheet_id, worksheet_name)
        return worksheet.get_all_records()

    def read_range(self, spreadsheet_id: str, range_name: str, worksheet_name: str = None) -> List[List]:
        """
        讀取指定範圍的資料

        Args:
            spreadsheet_id: Google Sheet 的 ID
            range_name: 範圍名稱 (例如: 'A1:C10')
            worksheet_name: 工作表名稱

        Returns:
            List[List]: 指定範圍的資料
        """
        worksheet = self.open_sheet(spreadsheet_id, worksheet_name)
        return worksheet.get(range_name)

    def write_data(self, spreadsheet_id: str, data: List[List],
                   start_cell: str = 'A1', worksheet_name: str = None):
        """
        寫入資料到工作表

        Args:
            spreadsheet_id: Google Sheet 的 ID
            data: 要寫入的資料 (二維列表)
            start_cell: 起始儲存格 (預設 'A1')
            worksheet_name: 工作表名稱
        """
        worksheet = self.open_sheet(spreadsheet_id, worksheet_name)
        worksheet.update(start_cell, data)

    def append_rows(self, spreadsheet_id: str, rows: List[List], worksheet_name: str = None):
        """
        在工作表末尾新增多行資料

        Args:
            spreadsheet_id: Google Sheet 的 ID
            rows: 要新增的資料行 (二維列表)
            worksheet_name: 工作表名稱
        """
        worksheet = self.open_sheet(spreadsheet_id, worksheet_name)
        worksheet.append_rows(rows)

    def clear_sheet(self, spreadsheet_id: str, worksheet_name: str = None):
        """
        清空工作表所有資料

        Args:
            spreadsheet_id: Google Sheet 的 ID
            worksheet_name: 工作表名稱
        """
        worksheet = self.open_sheet(spreadsheet_id, worksheet_name)
        worksheet.clear()

    def create_worksheet(self, spreadsheet_id: str, title: str, rows: int = 100, cols: int = 20):
        """
        在 Google Sheet 中建立新的工作表

        Args:
            spreadsheet_id: Google Sheet 的 ID
            title: 新工作表的名稱
            rows: 行數
            cols: 欄數

        Returns:
            worksheet: 新建立的 Worksheet 物件
        """
        spreadsheet = self.client.open_by_key(spreadsheet_id)
        return spreadsheet.add_worksheet(title=title, rows=rows, cols=cols)


# 便利函數
def get_sheets_client(credentials_path: Optional[str] = None) -> GoogleSheetsClient:
    """
    取得 Google Sheets 客戶端實例

    Args:
        credentials_path: Google Service Account JSON 憑證檔案路徑

    Returns:
        GoogleSheetsClient: Google Sheets 客戶端實例
    """
    return GoogleSheetsClient(credentials_path)
