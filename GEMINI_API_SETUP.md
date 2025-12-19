# Gemini API 設置說明

## 功能說明

本系統整合了 Google Gemini AI 來提供報告數據洞察功能。此功能**只能讀取報告數據**,不能讀取完整的原始監測數據。

## 設置步驟

### 1. 獲取 Gemini API Key

1. 前往 [Google AI Studio](https://aistudio.google.com/apikey)
2. 登入你的 Google 帳號
3. 點擊 "Get API Key" 創建新的 API key
4. 複製產生的 API key

### 2. 設置環境變量

#### Windows (開發環境)

1. 打開命令提示字元
2. 設置環境變量:
```bash
set GEMINI_API_KEY=你的API_KEY
```

或者在 PowerShell 中:
```powershell
$env:GEMINI_API_KEY="你的API_KEY"
```

#### Linux/Mac (生產環境)

在 `.bashrc` 或 `.zshrc` 中添加:
```bash
export GEMINI_API_KEY='你的API_KEY'
```

#### Django settings.py (替代方法)

你也可以直接在 `config/settings.py` 中添加:
```python
# Gemini AI 配置
GEMINI_API_KEY = '你的API_KEY'  # 不建議在生產環境中這樣做
```

**注意**: 為了安全,建議使用環境變量而不是直接寫在 settings.py 中。

### 3. 在 Zeabur 上設置環境變量

1. 登入 Zeabur 控制台
2. 選擇你的專案
3. 進入 "Variables" 設定
4. 添加新的環境變量:
   - Key: `GEMINI_API_KEY`
   - Value: 你的 API key
5. 儲存並重新部署

## 使用方式

1. 前往報告詳情頁面 (`/stations/reports/{report_id}/`)
2. 點擊右上角的 "🤖 生成 AI 洞察" 按鈕
3. 等待 AI 分析完成(通常需要幾秒鐘)
4. 查看生成的洞察內容

## AI 洞察功能特點

- ✅ **數據趨勢分析**: 分析報告中的主要趨勢和模式
- ✅ **異常值識別**: 指出任何異常或值得關注的數值
- ✅ **環境評估**: 評估海洋環境的整體健康狀況
- ✅ **建議事項**: 提供具體的監測建議或需要注意的事項

## 重要限制

⚠️ **此功能只能讀取報告數據,不能讀取完整的原始測站數據**

這是為了:
- 保護原始數據的隱私和安全
- 控制 API 使用成本
- 確保 AI 分析的範圍在合理的報告摘要內

## 故障排除

### 錯誤: "Gemini API 未配置"

- 檢查環境變量 `GEMINI_API_KEY` 是否正確設置
- 重新啟動 Django 服務器
- 確認 API key 沒有過期

### 錯誤: "生成洞察失敗"

- 檢查網路連線
- 確認 API key 仍然有效
- 查看 Django 日誌獲取詳細錯誤信息

### API 配額限制

Google Gemini API 有使用配額限制。如果超過限制,可能需要:
- 等待配額重置
- 升級到付費方案
- 查看 [Google AI Studio](https://aistudio.google.com/) 的配額使用情況

## 成本估算

- Gemini 2.0 Flash 模型提供免費配額
- 每月免費請求數: 1500 requests/day
- 詳細定價請參考: https://ai.google.dev/pricing

## 安全建議

1. **不要** 將 API key 提交到 git
2. **使用** 環境變量存儲 API key
3. **定期** 輪換 API key
4. **限制** API key 的使用範圍
5. **監控** API 使用情況

## 相關文件

- `analysis_tools/gemini_service.py` - Gemini API 整合服務
- `station_data/views.py` - 報告洞察 API 端點
- `templates/station_data/report_detail.html` - 報告詳情頁面

## 技術支援

如有問題,請查看:
- [Google Gemini API 文檔](https://ai.google.dev/docs)
- [Django 環境變量設置](https://docs.djangoproject.com/en/stable/topics/settings/)
