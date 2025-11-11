"""ocean_monitor\analysis_tools\chart_helpers.py 圖表數據轉換工具"""

def prepare_chart_data(readings):
    """準備圖表數據"""
    return {
        'labels': [r.timestamp.strftime('%m/%d %H:%M') for r in reversed(readings)],
        'temperature': [float(r.temperature) if r.temperature else None for r in reversed(readings)],
        'ph': [float(r.ph) if r.ph else None for r in reversed(readings)],
        'oxygen': [float(r.oxygen) if r.oxygen else None for r in reversed(readings)],
        'salinity': [float(r.salinity) if r.salinity else None for r in reversed(readings)],
    }