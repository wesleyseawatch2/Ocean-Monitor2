import os
from django.core.asgi import get_asgi_application

# 根據環境變數決定使用哪個 settings
# 在 Zeabur 上設定 DJANGO_ENV=production
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
    'config.settings.production' if os.getenv('DJANGO_ENV') == 'production'
    else 'config.settings.development'
)

# 必須在導入 WhiteNoise 之前設定 Django
django_application = get_asgi_application()

# 使用 WhiteNoise 包裝 ASGI application 來提供靜態檔案
from whitenoise import WhiteNoise
application = WhiteNoise(django_application, root=None)