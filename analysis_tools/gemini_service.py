# ocean_monitor\analysis_tools\gemini_service.py
"""
Gemini AI 整合服務
用於分析報告數據並提供洞察
"""
import os
import json
import google.generativeai as genai
from django.conf import settings


class GeminiInsightService:
    """Gemini AI 洞察服務"""

    def __init__(self):
        """初始化 Gemini API"""
        # 從環境變量或 settings 獲取 API key
        api_key = os.environ.get('GEMINI_API_KEY') or getattr(settings, 'GEMINI_API_KEY', None)

        if not api_key:
            raise ValueError("GEMINI_API_KEY 未設置。請在環境變量或 settings.py 中設置。")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

    def generate_report_insight(self, report):
        """
        為報告生成 AI 洞察

        Args:
            report: Report 模型實例

        Returns:
            dict: 包含洞察內容的字典
        """
        try:
            # 準備報告數據
            report_data = self._prepare_report_data(report)

            # 構建提示詞
            prompt = self._build_prompt(report, report_data)

            # 調用 Gemini API
            response = self.model.generate_content(prompt)

            # 解析響應
            insight = {
                'status': 'success',
                'content': response.text,
                'report_id': report.id,
                'report_type': report.report_type,
            }

            return insight

        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'report_id': report.id,
            }

    def _prepare_report_data(self, report):
        """準備報告數據供 AI 分析"""
        data = {
            'title': report.title,
            'report_type': report.get_report_type_display(),
            'status': report.get_status_display(),
            'summary': report.summary,
            'created_at': report.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'content': report.content,
        }
        return data

    def _build_prompt(self, report, report_data):
        """構建給 Gemini 的提示詞"""

        # 基本提示詞
        base_prompt = """你是一個專業的海洋數據分析專家。請分析以下海洋監測報告,並提供專業的數據洞察和建議。

報告資訊:
- 標題: {title}
- 類型: {report_type}
- 狀態: {status}
- 創建時間: {created_at}

報告摘要:
{summary}

報告詳細數據:
{content_json}

請從以下角度提供洞察:
1. **數據趨勢分析**: 分析數據中的主要趨勢和模式
2. **異常值識別**: 指出任何異常或值得關注的數值
3. **環境評估**: 評估海洋環境的整體健康狀況
4. **建議事項**: 提供具體的監測建議或需要注意的事項

請用繁體中文回答,保持專業但易懂的語言風格。回答要有條理,使用標題和分段。
"""

        # 格式化內容
        content_json = json.dumps(report_data['content'], ensure_ascii=False, indent=2)

        prompt = base_prompt.format(
            title=report_data['title'],
            report_type=report_data['report_type'],
            status=report_data['status'],
            created_at=report_data['created_at'],
            summary=report_data['summary'],
            content_json=content_json,
        )

        return prompt

    def generate_custom_insight(self, report_data, custom_question=None):
        """
        生成自定義洞察

        Args:
            report_data: 報告數據字典
            custom_question: 用戶的自定義問題

        Returns:
            dict: 洞察結果
        """
        try:
            # 構建自定義提示詞
            if custom_question:
                prompt = f"""你是一個專業的海洋數據分析專家。

報告數據:
{json.dumps(report_data, ensure_ascii=False, indent=2)}

用戶問題:
{custom_question}

請根據報告數據回答用戶的問題,保持專業但易懂的語言風格。請用繁體中文回答。
"""
            else:
                prompt = self._build_prompt(None, report_data)

            response = self.model.generate_content(prompt)

            return {
                'status': 'success',
                'content': response.text,
            }

        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
            }


# 創建單例實例
def get_gemini_service():
    """獲取 Gemini 服務實例"""
    try:
        return GeminiInsightService()
    except ValueError as e:
        # API key 未設置時返回 None
        print(f"Warning: {e}")
        return None
