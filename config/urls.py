from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 首頁直接導向通用登入頁面
    path('', RedirectView.as_view(url='/login/', permanent=False)),

    # 通用登入 (core app)
    path('', include('apps.core.urls')),

    # Django Admin (用於管理 Celery Beat 定時任務)
    path('admin/', admin.site.urls),

    # 自訂後台
    path('panel/', include('admin_panel.urls')),

    # 其他功能
    path('accounts/', include('allauth.urls')),  # allauth 的所有 URLs (Google登入)
    path('stations/', include('station_data.urls')),  # 測站資料頁面
]+static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# 在生產環境使用 WhiteNoise 提供靜態檔案
# 在開發環境使用 Django 內建靜態檔案服務
#if settings.DEBUG:
#    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)