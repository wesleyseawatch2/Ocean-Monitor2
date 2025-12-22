"""
資料去識別化工具
用於處理報告數據中的敏感信息
"""
import re
import copy


def anonymize_report_data(data):
    """
    對報告數據進行去識別化處理

    移除或替換可能識別特定測站或位置的資訊:
    - 測站名稱 -> 測站代碼
    - 地點名稱 -> 通用描述
    - GPS 座標 -> 移除精確值
    """
    # 深拷貝避免修改原始數據
    anonymized_data = copy.deepcopy(data)

    # 建立測站名稱映射表
    station_mapping = {}
    station_counter = [1]  # 使用列表以便在嵌套函數中修改

    def anonymize_text(text):
        """去識別化文字內容"""
        if not isinstance(text, str):
            return text

        # 替換測站名稱 (例如: ChaoJingCR1000X -> 測站A)
        station_pattern = r'[A-Za-z]+CR1000X?'
        stations_found = re.findall(station_pattern, text)
        for station in stations_found:
            if station not in station_mapping:
                station_mapping[station] = f"測站{chr(64 + station_counter[0])}"  # 測站A, 測站B, ...
                station_counter[0] += 1
            text = text.replace(station, station_mapping[station])

        # 替換地點名稱 (常見地名)
        location_patterns = {
            r'潮境': '地點1',
            r'碧砂': '地點2',
            r'正濱': '地點3',
            r'基隆': '北部海域',
            r'台北': '北部地區',
            r'新北': '北部地區',
        }
        for pattern, replacement in location_patterns.items():
            text = re.sub(pattern, replacement, text)

        # 移除 GPS 座標 (例如: 25.123456, 121.654321)
        text = re.sub(r'\d+\.\d{4,}', '[已移除]', text)
        text = re.sub(r'緯度[:：]\s*\d+\.\d+', '緯度: [已移除]', text)
        text = re.sub(r'經度[:：]\s*\d+\.\d+', '經度: [已移除]', text)

        return text

    def anonymize_dict(obj):
        """遞迴處理字典"""
        if isinstance(obj, dict):
            result = {}
            for key, value in obj.items():
                # 特定鍵值的處理
                if key in ['station_name', 'station_id']:
                    if isinstance(value, str) and value:
                        if value not in station_mapping:
                            station_mapping[value] = f"測站{chr(64 + station_counter[0])}"
                            station_counter[0] += 1
                        result[key] = station_mapping[value]
                    elif isinstance(value, int):
                        station_id = f"station_{value}"
                        if station_id not in station_mapping:
                            station_mapping[station_id] = f"測站{chr(64 + station_counter[0])}"
                            station_counter[0] += 1
                        result[key] = station_mapping[station_id]
                    else:
                        result[key] = value
                elif key in ['location', 'station_location']:
                    result[key] = '海域監測點'
                elif key in ['latitude', 'longitude']:
                    result[key] = '[已移除]'
                else:
                    result[key] = anonymize_dict(value)
            return result
        elif isinstance(obj, list):
            return [anonymize_dict(item) for item in obj]
        elif isinstance(obj, str):
            return anonymize_text(obj)
        else:
            return obj

    # 處理標題、摘要和內容
    anonymized_data['title'] = anonymize_text(anonymized_data['title'])
    anonymized_data['summary'] = anonymize_text(anonymized_data['summary'])
    anonymized_data['content'] = anonymize_dict(anonymized_data['content'])

    # 添加去識別化標記
    anonymized_data['anonymized'] = True
    anonymized_data['anonymization_note'] = '本報告已進行去識別化處理，移除了測站名稱、地點資訊和 GPS 座標等可識別資訊。'

    return anonymized_data
