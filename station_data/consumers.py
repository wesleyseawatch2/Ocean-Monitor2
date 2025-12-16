"""
WebSocket consumers for real-time station data updates
"""
import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from data_ingestion.models import Station, Reading


class StationReadingConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for broadcasting real-time sensor readings
    """

    async def connect(self):
        """處理 WebSocket 連接"""
        # 從 URL 中獲取 station_id（如果有的話）
        self.station_id = self.scope['url_route'].get('kwargs', {}).get('station_id')

        if self.station_id:
            # 單一測站的即時資料
            self.group_name = f'station_{self.station_id}'
        else:
            # 所有測站的即時資料
            self.group_name = 'all_stations'

        # 加入群組
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # 接受 WebSocket 連接
        await self.accept()

        # 連接後立即發送當前資料
        await self.send_current_data()

    async def disconnect(self, close_code):
        """處理 WebSocket 斷開連接"""
        # 離開群組
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """接收來自 WebSocket 的訊息（目前不需要處理）"""
        pass

    async def sensor_reading_update(self, event):
        """
        從群組接收訊息並發送到 WebSocket
        """
        # 發送訊息到 WebSocket
        await self.send(text_data=json.dumps(event['data']))

    async def send_current_data(self):
        """發送當前資料到客戶端"""
        try:
            if self.station_id:
                # 獲取單一測站的最新資料
                data = await self.get_station_latest_data(self.station_id)
            else:
                # 獲取所有測站的最新資料
                data = await self.get_all_stations_latest_data()

            await self.send(text_data=json.dumps({
                'type': 'initial_data',
                'data': data
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    @database_sync_to_async
    def get_station_latest_data(self, station_id):
        """獲取單一測站的最新資料"""
        try:
            station = Station.objects.get(id=station_id)
            latest_reading = station.readings.order_by('-timestamp').first()

            if latest_reading:
                return {
                    'station_id': station.id,
                    'station_name': station.station_name,
                    'timestamp': latest_reading.timestamp.isoformat(),
                    'temperature': float(latest_reading.temperature) if latest_reading.temperature else None,
                    'ph': float(latest_reading.ph) if latest_reading.ph else None,
                    'dissolved_oxygen': float(latest_reading.oxygen) if latest_reading.oxygen else None,
                    'salinity': float(latest_reading.salinity) if latest_reading.salinity else None,
                    'conductivity': float(latest_reading.conductivity) if latest_reading.conductivity else None,
                    'pressure': float(latest_reading.pressure) if latest_reading.pressure else None,
                    'fluorescence': float(latest_reading.fluorescence) if latest_reading.fluorescence else None,
                    'turbidity': float(latest_reading.turbidity) if latest_reading.turbidity else None,
                }
            return None
        except Station.DoesNotExist:
            return None

    @database_sync_to_async
    def get_all_stations_latest_data(self):
        """獲取所有測站的最新資料"""
        stations_data = []
        stations = Station.objects.all()

        for station in stations:
            latest_reading = station.readings.order_by('-timestamp').first()
            if latest_reading:
                stations_data.append({
                    'station_id': station.id,
                    'station_name': station.station_name,
                    'timestamp': latest_reading.timestamp.isoformat(),
                    'temperature': float(latest_reading.temperature) if latest_reading.temperature else None,
                    'ph': float(latest_reading.ph) if latest_reading.ph else None,
                    'dissolved_oxygen': float(latest_reading.oxygen) if latest_reading.oxygen else None,
                    'salinity': float(latest_reading.salinity) if latest_reading.salinity else None,
                })

        return stations_data
