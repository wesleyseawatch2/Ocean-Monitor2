from pathlib import Path
import os
from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv()   

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'your-default-secret-key')


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # allauth 需要

    # Custom apps
    'data_ingestion',
    'station_data',
    'analysis_tools',
    'apps.core',
    'apps.core.accounts',
    'admin_panel',  # 自訂後台

    # Third-party
    'channels',  # ASGI / WebSocket 支援
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',  # Google 登入
    'django_celery_beat',  # Celery Beat 動態排程
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # WhiteNoise 靜態檔案服務
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # allauth 必要的 middleware
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.static',  # 靜態文件上下文處理器
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'zh-hant'

TIME_ZONE = 'Asia/Taipei'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise 靜態檔案配置 (Django 4.2+ 使用 STORAGES)
# 在生產環境使用 CompressedStaticFilesStorage (不使用 Manifest，避免部署問題)
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 自訂使用者模型
AUTH_USER_MODEL = 'accounts.User'

# Django Sites Framework (allauth 需要)
SITE_ID = 1

# 認證後端設定
AUTHENTICATION_BACKENDS = [
    # Django 預設的認證後端
    'django.contrib.auth.backends.ModelBackend',
    # allauth 的認證後端 (支援社交登入)
    'allauth.account.auth_backends.AuthenticationBackend',
]

# django-allauth 設定
ACCOUNT_ADAPTER = 'apps.core.adapters.CustomAccountAdapter'  # 使用自訂適配器
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'  # 允許使用 username 或 email 登入
ACCOUNT_EMAIL_REQUIRED = True  # 註冊時必須填寫 email
ACCOUNT_EMAIL_VERIFICATION = 'optional'  # email 驗證為選填 (可改為 'mandatory' 強制驗證)
ACCOUNT_USERNAME_REQUIRED = False  # 社交登入不需要 username，使用 email 即可
LOGIN_REDIRECT_URL = '/login/'  # 預設登入後導向 (會被 adapter 覆寫)
LOGOUT_REDIRECT_URL = '/login/'  # 登出後導向登入頁

# 社交登入設定
SOCIALACCOUNT_AUTO_SIGNUP = True  # 使用社交登入時自動建立帳號
SOCIALACCOUNT_QUERY_EMAIL = True  # 向社交平台請求 email
SOCIALACCOUNT_LOGIN_ON_GET = True  # 直接重定向到 OAuth 頁面，跳過中間確認頁面
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True  # 允許使用 email 進行社交帳號認證
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True  # 自動連結相同 email 的既有帳號

# Google OAuth 設定：指定要取得的資訊範圍
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',  # 取得個人資料（名字、頭像等）
            'email',    # 取得 email
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',  # 不需要 refresh token
        },
        'FETCH_USERINFO': True,  # 從 Google 取得用戶資訊
    }
}

# ==========================================
# Redis 連線設定
# ==========================================
REDIS_URI = os.getenv('REDIS_URI', 'redis://127.0.0.1:6379/1')

# ==========================================
# Celery 設定 - 使用 Redis 作為 Broker
# ==========================================
# Broker：任務佇列存放的地方（使用 Redis）
CELERY_BROKER_URL = REDIS_URI

# Result Backend：任務結果存放的地方（可選，這裡也用 Redis）
CELERY_RESULT_BACKEND = REDIS_URI

# 時區設定（與 Django 一致）
CELERY_TIMEZONE = TIME_ZONE

# 接受的內容類型
CELERY_ACCEPT_CONTENT = ['json']

# 任務序列化格式
CELERY_TASK_SERIALIZER = 'json'

# 結果序列化格式
CELERY_RESULT_SERIALIZER = 'json'

# 啟動時重試連線（消除 Celery 6.0 棄用警告）
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# ==========================================
# Cache 設定 - 使用 Redis
# ==========================================
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URI,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'library',  # 所有 key 都會加上這個前綴
        'TIMEOUT': 300,  # 預設快取時間 5 分鐘（單位：秒）
    }
}

# ==========================================
# Channels 設定 - WebSocket 層使用 Redis
# ==========================================
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [REDIS_URI],
        },
    },
}

# ==========================================
# Celery Beat 定時任務設定 - 使用 django-celery-beat
# ==========================================

# 使用 django-celery-beat 的資料庫排程器
# 這樣可以透過 Django Admin 或程式碼動態管理排程，不需要重啟服務
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# 預設的靜態排程（可選）
# 如果需要固定的全域排程，可以保留這個設定
# django-celery-beat 會同時執行資料庫排程和靜態排程
CELERY_BEAT_SCHEDULE = {
    # 每小時更新海洋數據（全域任務）
    'hourly-ocean-data-update': {
        'task': 'station_data.tasks.update_ocean_data_from_source',
        'schedule': crontab(minute=0),  # 每小時的第 0 分鐘執行
    },

    # 每 6 小時檢查數據異常（全域任務）
    'check-ocean-alerts': {
        'task': 'station_data.tasks.check_ocean_data_alerts',
        'schedule': crontab(minute=0, hour='*/6'),  # 每 6 小時執行
    },

    # 每天早上 8 點產生統計報告（全域任務）
    'daily-statistics': {
        'task': 'station_data.tasks.generate_daily_statistics',
        'schedule': crontab(hour=8, minute=0),  # 每天早上 8 點
    },

    # 測試用：每 2 分鐘執行一次（開發測試用，正式環境請移除或註解）
    'test-update-every-2-minutes': {
        'task': 'station_data.tasks.update_ocean_data_from_source',
        'schedule': 120.0,  # 每 120 秒（2 分鐘）
    },
}
