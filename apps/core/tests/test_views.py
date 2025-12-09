"""
core.views 測試 - 登入功能測試
"""
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


# ==========================================
# 登入頁面測試（未登入）
# ==========================================

def test_login_page_status_code(client):
    """測試登入頁面回應狀態碼"""
    response = client.get(reverse('core:login'))
    assert response.status_code == 200


def test_login_page_template(client):
    """測試使用的 template"""
    response = client.get(reverse('core:login'))
    assert 'core/login.html' in [t.name for t in response.templates]


# ==========================================
# 已登入使用者重定向測試
# ==========================================

def test_logged_in_user_redirect_to_stations(authenticated_client):
    """測試已登入的一般使用者會被重定向到 /stations/"""
    response = authenticated_client.get(reverse('core:login'))

    assert response.status_code == 302
    assert response.url == '/stations/'


def test_logged_in_staff_redirect_to_panel(staff_authenticated_client):
    """測試已登入的管理員會被重定向到 /panel/"""
    response = staff_authenticated_client.get(reverse('core:login'))

    assert response.status_code == 302
    assert response.url == '/panel/'


# ==========================================
# POST 登入測試（一般使用者）
# ==========================================

def test_login_with_valid_credentials(client, user):
    """測試正確的帳號密碼可以登入"""
    response = client.post(reverse('core:login'), {
        'username': 'testuser',
        'password': 'testpass123'
    })

    assert response.status_code == 302
    assert response.url == '/stations/'

    # 確認使用者已登入
    assert '_auth_user_id' in client.session


def test_login_with_invalid_password(client, user):
    """測試錯誤密碼會顯示錯誤訊息"""
    response = client.post(reverse('core:login'), {
        'username': 'testuser',
        'password': 'wrongpassword'
    })

    # 不應該重定向
    assert response.status_code == 200

    # 確認有錯誤訊息
    messages = list(response.context['messages'])
    assert len(messages) > 0
    assert '帳號或密碼錯誤' in str(messages[0])


def test_login_with_nonexistent_user(client):
    """測試不存在的帳號會顯示錯誤訊息"""
    response = client.post(reverse('core:login'), {
        'username': 'nonexistent',
        'password': 'somepassword'
    })

    assert response.status_code == 200

    messages = list(response.context['messages'])
    assert '帳號或密碼錯誤' in str(messages[0])


# ==========================================
# POST 登入測試（管理員）
# ==========================================

def test_staff_login_redirect_to_panel(client, staff_user):
    """測試管理員登入後會被重定向到 /panel/"""
    response = client.post(reverse('core:login'), {
        'username': 'adminuser',
        'password': 'adminpass123'
    })

    assert response.status_code == 302
    assert response.url == '/panel/'


def test_staff_login_success_message(client, staff_user):
    """測試管理員登入成功訊息"""
    response = client.post(reverse('core:login'), {
        'username': 'adminuser',
        'password': 'adminpass123'
    }, follow=True)

    messages = list(response.context['messages'])
    assert len(messages) > 0
    assert '歡迎回來' in str(messages[0])
    assert 'adminuser' in str(messages[0])


def test_normal_user_login_success_message(client, user):
    """測試一般使用者登入成功訊息"""
    response = client.post(reverse('core:login'), {
        'username': 'testuser',
        'password': 'testpass123'
    }, follow=True)

    messages = list(response.context['messages'])
    assert len(messages) > 0
    assert '歡迎' in str(messages[0])
    assert 'testuser' in str(messages[0])


# ==========================================
# 表單欄位測試
# ==========================================

def test_login_with_missing_username(client):
    """測試缺少 username 欄位"""
    response = client.post(reverse('core:login'), {
        'password': 'testpass123'
    })

    assert response.status_code == 200
    messages = list(response.context['messages'])
    assert '帳號或密碼錯誤' in str(messages[0])


def test_login_with_missing_password(client, user):
    """測試缺少 password 欄位"""
    response = client.post(reverse('core:login'), {
        'username': 'testuser'
    })

    assert response.status_code == 200
    messages = list(response.context['messages'])
    assert '帳號或密碼錯誤' in str(messages[0])


def test_login_with_empty_credentials(client):
    """測試空白的帳號密碼"""
    response = client.post(reverse('core:login'), {
        'username': '',
        'password': ''
    })

    assert response.status_code == 200


# ==========================================
# GET vs POST 測試
# ==========================================

def test_login_get_request_shows_form(client):
    """測試 GET 請求會顯示登入表單"""
    response = client.get(reverse('core:login'))

    assert response.status_code == 200
    assert 'core/login.html' in [t.name for t in response.templates]


def test_login_post_request_processes_form(client, user):
    """測試 POST 請求會處理登入"""
    response = client.post(reverse('core:login'), {
        'username': 'testuser',
        'password': 'testpass123'
    })

    assert response.status_code == 302
