"""統計分析函數"""


def calculate_average(values):
    """計算平均值"""
    if not values:
        return None
    return sum(values) / len(values)


def calculate_min_max(values):
    """計算最小值和最大值"""
    if not values:
        return None, None
    return min(values), max(values)


def calculate_statistics(readings, field_name):
    """計算特定欄位的統計資料"""
    values = [getattr(r, field_name) for r in readings if getattr(r, field_name) is not None]
    
    if not values:
        return {
            'count': 0,
            'avg': None,
            'min': None,
            'max': None
        }
    
    return {
        'count': len(values),
        'avg': round(sum(values) / len(values), 2),
        'min': min(values),
        'max': max(values)
    }