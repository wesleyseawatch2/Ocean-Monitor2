"""
WebSocket URL routing for station_data app
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # 所有測站的即時資料
    re_path(r'ws/stations/readings/$', consumers.StationReadingConsumer.as_asgi()),

    # 特定測站的即時資料
    re_path(r'ws/stations/(?P<station_id>\d+)/$', consumers.StationReadingConsumer.as_asgi()),
]
