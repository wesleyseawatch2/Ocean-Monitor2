from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# 開發環境使用預設的靜態檔案儲存 (不壓縮)
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'