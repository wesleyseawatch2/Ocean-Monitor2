import os

# 根據環境變數決定使用哪個 settings
# 在 Zeabur 上設定 DJANGO_ENV=production
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
    'config.settings.production' if os.getenv('DJANGO_ENV') == 'production'
    else 'config.settings.development'
)

# 導入 Django 和 Channels
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# 必須在 ProtocolTypeRouter 之前初始化 Django
django_asgi_app = get_asgi_application()

# 導入 WebSocket routing
from station_data.routing import websocket_urlpatterns

# ASGI 應用程式：支援 HTTP 和 WebSocket
# WhiteNoise 透過 Django middleware 層處理靜態文件
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})