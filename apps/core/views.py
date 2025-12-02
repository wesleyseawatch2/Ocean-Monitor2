# apps/core/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages


def home_login(request):
    """
    首頁登入頁面 - 支援一般登入和 Google 登入
    """
    # 如果已登入,根據權限導向不同頁面
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('/panel/')  # 管理員 → 後台
        else:
            return redirect('/stations/')  # 一般使用者 → 測站頁面

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_staff:
                messages.success(request, f'歡迎回來, {user.username}!')
                return redirect('/panel/')
            else:
                messages.success(request, f'歡迎, {user.username}!')
                return redirect('/stations/')
        else:
            messages.error(request, '帳號或密碼錯誤')

    return render(request, 'core/login.html')
