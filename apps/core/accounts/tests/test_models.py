"""
User Model 測試 - pytest 風格
"""
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


# ==========================================
# User 建立測試
# ==========================================

def test_user_creation(user):
    """測試使用者建立"""
    assert user.username == 'testuser'
    assert user.email == 'test@example.com'
    assert user.check_password('testpass123')


def test_staff_user_creation(staff_user):
    """測試管理員使用者建立"""
    assert staff_user.username == 'adminuser'
    assert staff_user.is_staff is True
    assert staff_user.check_password('adminpass123')


def test_user_str_method(user):
    """測試 __str__ 方法"""
    assert str(user) == 'testuser'


# ==========================================
# User 自訂欄位測試
# ==========================================

def test_user_custom_fields(db):
    """測試自訂欄位（電話、頭像、個人簡介）"""
    user = User.objects.create_user(
        username='customuser',
        email='custom@example.com',
        password='pass123',
        phone='0912345678',
        bio='這是我的個人簡介'
    )

    assert user.phone == '0912345678'
    assert user.bio == '這是我的個人簡介'
    assert not user.avatar  # 空白，因為沒上傳


def test_user_optional_fields_can_be_blank(db):
    """測試選填欄位可以留空"""
    user = User.objects.create_user(
        username='minimaluser',
        email='minimal@example.com',
        password='pass123'
    )

    assert user.phone == ''
    assert user.bio == ''
    assert not user.avatar


# ==========================================
# 使用者權限測試
# ==========================================

def test_normal_user_is_not_staff(user):
    """測試一般使用者不是 staff"""
    assert user.is_staff is False
    assert user.is_superuser is False


def test_create_superuser(db):
    """測試建立超級使用者"""
    superuser = User.objects.create_superuser(
        username='superuser',
        email='super@example.com',
        password='superpass123'
    )

    assert superuser.is_staff is True
    assert superuser.is_superuser is True
    assert superuser.is_active is True


# ==========================================
# 使用者查詢測試
# ==========================================

def test_user_queryset(db, user, staff_user):
    """測試使用者查詢"""
    all_users = User.objects.all()
    assert all_users.count() == 2

    staff_users = User.objects.filter(is_staff=True)
    assert staff_users.count() == 1
    assert staff_users.first().username == 'adminuser'


def test_user_authentication(user):
    """測試使用者認證"""
    # 正確密碼
    assert user.check_password('testpass123') is True

    # 錯誤密碼
    assert user.check_password('wrongpassword') is False
