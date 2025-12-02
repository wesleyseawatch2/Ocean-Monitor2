from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import resolve_url


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    自訂帳號適配器
    根據使用者權限導向不同頁面
    """
    def get_login_redirect_url(self, request):
        """
        登入後重定向邏輯
        """
        user = request.user
        if user.is_staff:
            # 管理員 → 後台
            return '/panel/'
        else:
            # 一般使用者 → 測站頁面
            return '/stations/'
