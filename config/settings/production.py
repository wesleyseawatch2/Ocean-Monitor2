# config/settings/production.py

from .base import *
import os
from dotenv import load_dotenv
import dj_database_url

# 載入 .env 檔案 (如果存在)
load_dotenv()

DEBUG = os.getenv('DEBUG', 'False') == 'True'  # 可透過環境變數控制

# 從環境變數讀取允許的主機
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')

# 資料庫設定
# Zeabur 會自動注入 POSTGRES_CONNECTION_STRING
postgres_connection_string = os.getenv('POSTGRES_CONNECTION_STRING')

if postgres_connection_string:
    # 在 Zeabur 上使用 PostgreSQL
    DATABASES = {
        'default': dj_database_url.parse(
            postgres_connection_string,
            conn_max_age=600  # 連線池:連線最多保持 600 秒
        )
    }
else:
    # 本地開發使用 SQLite (fallback)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# 靜態檔案設定已在 base.py 中配置 (使用 WhiteNoise)

# 生產環境安全設定 (在 Zeabur 上先關閉 HTTPS 重定向,測試靜態檔案)
SECURE_SSL_REDIRECT = False  # 暫時關閉,確認靜態檔案正常後再開啟
SESSION_COOKIE_SECURE = False  # 暫時關閉
CSRF_COOKIE_SECURE = False  # 暫時關閉

# 信任 Zeabur 的代理伺服器
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

CSRF_TRUSTED_ORIGINS = [
    "https://ocean-monitor2.zeabur.app",
]

# ==========================================
# Channels 設定 - 在 Zeabur 上使用內存通道層
# ==========================================
# 注意：內存通道層只適合單一進程，不支援多個 worker
# 如果需要擴展，請在 Zeabur 上添加 Redis 服務
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# 日誌配置 - 在生產環境中輸出詳細錯誤訊息
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.template': {
            'handlers': ['console'],
            'level': 'DEBUG',  # 詳細記錄模板錯誤
            'propagate': False,
        },
    },
}
