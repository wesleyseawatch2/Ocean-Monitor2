from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = 'django-insecure-your-secret-key-here'

DEBUG = True

ALLOWED_HOSTS = []

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

    # allauth 相關
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',  # Google 登入
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
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
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

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

STATIC_URL = 'static/'

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
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'  # 允許使用 username 或 email 登入
ACCOUNT_EMAIL_REQUIRED = True  # 註冊時必須填寫 email
ACCOUNT_EMAIL_VERIFICATION = 'optional'  # email 驗證為選填 (可改為 'mandatory' 強制驗證)
ACCOUNT_USERNAME_REQUIRED = False  # 社交登入不需要 username，使用 email 即可
LOGIN_REDIRECT_URL = '/'  # 登入後導向首頁
LOGOUT_REDIRECT_URL = '/'  # 登出後導向首頁

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