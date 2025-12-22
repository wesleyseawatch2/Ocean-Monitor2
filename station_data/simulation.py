"""
海洋數據模擬引擎

模擬真實的海洋環境數據變化，包括溫度、鹽度、溶氧等參數的自然波動
"""
import random
from datetime import datetime
from decimal import Decimal
from data_ingestion.models import Station, Reading
from django.utils import timezone


class OceanDataSimulator:
    """
    模擬海洋數據的類別

    特點：
    - 溫度：以日週期變化，正午最高，午夜最低
    - 鹽度：相對穩定，略有波動
    - 溶氧：與溫度和光照反相關
    - pH：略有波動，保持在海水正常範圍
    - GPS：在測站附近海域漂移（模擬儀器移動）
    """

    # 基礎參數範圍（可依測站位置調整）
    BASE_TEMP = 25.0  # 基礎溫度
    BASE_SALINITY = 33.5  # 基礎鹽度
    BASE_OXYGEN = 8.0  # 基礎溶氧
    BASE_PH = 8.2  # 基礎 pH
    BASE_CONDUCTIVITY = 54000.0  # 基礎電導率

    # 波動幅度
    TEMP_AMPLITUDE = 3.0  # 溫度波動 ±3°C
    SALINITY_AMPLITUDE = 0.5  # 鹽度波動 ±0.5
    OXYGEN_AMPLITUDE = 1.5  # 溶氧波動 ±1.5
    pH_AMPLITUDE = 0.3  # pH 波動 ±0.3

    # GPS 漂移參數
    GPS_DRIFT_RANGE = 0.003  # GPS 漂移範圍 ±0.003 度 (約 300 公尺)

    def __init__(self, station=None):
        """
        初始化模擬器

        Args:
            station: Station 實例，用於根據測站位置調整參數
        """
        self.current_hour = timezone.now().hour
        self.current_minute = timezone.now().minute
        self.station = station

        # 根據測站位置微調基礎參數（模擬不同海域的差異）
        if station and station.latitude:
            # 根據緯度調整溫度（越靠近赤道越熱）
            lat = float(station.latitude)
            # 台灣附近緯度約 22-25 度
            self.base_temp_offset = (25 - abs(lat)) * 0.5  # 緯度每偏離 1 度，溫度變化 0.5°C
        else:
            self.base_temp_offset = 0
        
    def calculate_diurnal_factor(self):
        """
        計算日週期係數 (0-1)
        中午 = 1.0，午夜 = 0.0
        """
        hour = timezone.now().hour
        # 使用正弦波表示日週期
        import math
        return (math.sin((hour - 6) * math.pi / 12) + 1) / 2
    
    def generate_temperature(self):
        """
        根據時間和測站位置生成溫度值

        考慮因素：
        - 日週期變化（白天較熱，夜間較冷）
        - 測站緯度（影響基礎溫度）
        - 隨機波動
        """
        diurnal = self.calculate_diurnal_factor()
        # 日間溫度較高，夜間較低
        variation = diurnal * self.TEMP_AMPLITUDE
        random_noise = random.uniform(-0.5, 0.5)
        temperature = self.BASE_TEMP + self.base_temp_offset + variation + random_noise
        return round(Decimal(str(temperature)), 2)
    
    def generate_salinity(self):
        """生成鹽度值"""
        variation = random.uniform(-self.SALINITY_AMPLITUDE, self.SALINITY_AMPLITUDE)
        salinity = self.BASE_SALINITY + variation
        return round(Decimal(str(salinity)), 4)
    
    def generate_oxygen(self):
        """生成溶氧值（與溫度反相關）"""
        diurnal = self.calculate_diurnal_factor()
        # 溫度高時溶氧低，溫度低時溶氧高
        variation = (1 - diurnal) * self.OXYGEN_AMPLITUDE
        random_noise = random.uniform(-0.3, 0.3)
        oxygen = self.BASE_OXYGEN + variation + random_noise
        return round(Decimal(str(max(oxygen, 4.0))), 3)  # 至少 4.0 mg/L
    
    def generate_ph(self):
        """生成 pH 值"""
        variation = random.uniform(-self.pH_AMPLITUDE, self.pH_AMPLITUDE)
        ph = self.BASE_PH + variation
        return round(Decimal(str(ph)), 2)
    
    def generate_pressure(self):
        """生成壓力值（相對穩定）"""
        # 海水壓力 = 深度 / 10 bar，這裡假設在 6 米深
        pressure = Decimal('0.6') + Decimal(str(random.uniform(-0.05, 0.05)))
        return round(pressure, 3)
    
    def generate_conductivity(self):
        """生成電導率值"""
        variation = random.uniform(-500, 500)
        conductivity = self.BASE_CONDUCTIVITY + variation
        return round(Decimal(str(conductivity)), 2)
    
    def generate_fluorescence(self):
        """生成螢光值（葉綠素濃度）"""
        diurnal = self.calculate_diurnal_factor()
        # 日間光合作用較強，螢光值較高
        variation = diurnal * 1.0
        random_noise = random.uniform(-0.2, 0.2)
        fluorescence = 0.5 + variation + random_noise
        return round(Decimal(str(max(fluorescence, 0.0))), 3)
    
    def generate_turbidity(self):
        """生成濁度值"""
        # 濁度通常在 3-8 之間，隨機波動
        turbidity = random.uniform(3.0, 8.0)
        return round(Decimal(str(turbidity)), 3)

    def generate_gps_with_drift(self, base_lat, base_lng):
        """
        生成帶有漂移的 GPS 座標（模擬移動中的儀器）

        模擬海上浮標或移動式監測設備在海流影響下的漂移。
        漂移方向和距離是隨機的，但保持在測站附近海域。

        Args:
            base_lat: 基礎緯度（測站登記位置）
            base_lng: 基礎經度（測站登記位置）

        Returns:
            (latitude, longitude) tuple

        漂移範圍說明：
            - ±0.003 度約等於 ±330 公尺
            - 確保儀器在測站附近的合理範圍內漂移
            - 適合模擬浮標、漂流監測器等設備
        """
        if not base_lat or not base_lng:
            return (None, None)

        # 模擬儀器在基礎位置附近漂移
        # 漂移範圍約 ±0.003 度 (約 300-330 公尺，適合海上監測設備)
        lat_drift = random.uniform(-self.GPS_DRIFT_RANGE, self.GPS_DRIFT_RANGE)
        lng_drift = random.uniform(-self.GPS_DRIFT_RANGE, self.GPS_DRIFT_RANGE)

        new_lat = base_lat + lat_drift
        new_lng = base_lng + lng_drift

        return (
            round(Decimal(str(new_lat)), 6),
            round(Decimal(str(new_lng)), 6)
        )

    def generate_reading(self, station):
        """
        生成完整的一筆數據記錄

        Args:
            station: Station 實例

        Returns:
            Reading 實例（已保存到資料庫）
        """
        # 如果測站有基礎座標,生成帶漂移的位置
        latitude, longitude = None, None
        if station.latitude and station.longitude:
            latitude, longitude = self.generate_gps_with_drift(
                float(station.latitude),
                float(station.longitude)
            )

        reading = Reading.objects.create(
            station=station,
            timestamp=timezone.now(),
            temperature=self.generate_temperature(),
            conductivity=self.generate_conductivity(),
            pressure=self.generate_pressure(),
            oxygen=self.generate_oxygen(),
            ph=self.generate_ph(),
            fluorescence=self.generate_fluorescence(),
            turbidity=self.generate_turbidity(),
            salinity=self.generate_salinity(),
            latitude=latitude,
            longitude=longitude,
        )
        return reading


def simulate_data_for_all_stations():
    """
    為所有測站生成模擬數據

    這個函數會：
    1. 查詢所有測站
    2. 為每個測站創建專屬的 OceanDataSimulator 實例
    3. 根據測站的地理位置（緯度）調整數據參數
    4. 生成帶有 GPS 漂移的監測數據（模擬海上移動設備）

    Returns:
        包含生成結果的字典
        {
            'status': 'success' 或 'error',
            'count': 生成的數據筆數,
            'readings': 數據記錄列表,
            'timestamp': 生成時間
        }
    """
    stations = Station.objects.all()

    if not stations.exists():
        return {
            'status': 'error',
            'message': '沒有找到任何測站',
            'count': 0
        }

    created_readings = []

    for station in stations:
        # 為每個測站創建專屬的模擬器實例
        # 這樣每個測站會有不同的基礎參數（例如根據緯度調整的溫度）
        simulator = OceanDataSimulator(station=station)
        reading = simulator.generate_reading(station)

        created_readings.append({
            'station_id': station.id,
            'station_name': station.station_name,
            'location': station.location,
            'reading_id': reading.id,
            'timestamp': reading.timestamp.isoformat(),
            'temperature': float(reading.temperature),
            'ph': float(reading.ph),
            'oxygen': float(reading.oxygen),
            'salinity': float(reading.salinity),
            'latitude': float(reading.latitude) if reading.latitude else None,
            'longitude': float(reading.longitude) if reading.longitude else None,
        })

    return {
        'status': 'success',
        'count': len(created_readings),
        'readings': created_readings,
        'timestamp': timezone.now().isoformat(),
    }
