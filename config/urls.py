from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from django.conf import settings
from django.views.static import serve

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
]

# 在生產環境中手動添加靜態文件服務
# Django 的 static() 在 DEBUG=False 時不工作，所以我們手動添加
urlpatterns += [
    re_path(r'^static/(?P<path>.*)$', serve, {
        'document_root': settings.STATIC_ROOT,
    }),
]