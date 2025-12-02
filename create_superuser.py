"""
建立 Django 超級使用者

使用方式：
python create_superuser.py
"""
import os
import django

# 設定 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 60)
print("建立 Django 超級使用者")
print("=" * 60)
print()

# 檢查是否已有超級使用者
if User.objects.filter(is_superuser=True).exists():
    print("[提示] 系統中已存在超級使用者：")
    superusers = User.objects.filter(is_superuser=True)
    for user in superusers:
        print(f"  - {user.username} ({user.email})")
    print()
    choice = input("是否要建立新的超級使用者？ (y/n): ")
    if choice.lower() != 'y':
        print("\n[取消] 已取消建立")
        exit(0)

print("\n請輸入超級使用者資訊：")
print("-" * 60)

username = input("使用者名稱 (Username): ")
email = input("電子郵件 (Email，可留空): ")
password = input("密碼 (Password): ")
password_confirm = input("確認密碼 (Confirm): ")

# 驗證密碼
if password != password_confirm:
    print("\n[錯誤] 兩次輸入的密碼不一致！")
    exit(1)

if len(password) < 8:
    print("\n[錯誤] 密碼長度至少 8 個字元！")
    exit(1)

# 建立超級使用者
try:
    user = User.objects.create_superuser(
        username=username,
        email=email if email else None,
        password=password
    )
    print()
    print("=" * 60)
    print("[成功] 超級使用者建立成功！")
    print("=" * 60)
    print(f"\n使用者名稱: {user.username}")
    print(f"電子郵件: {user.email if user.email else '(未設定)'}")
    print()
    print("您現在可以使用此帳號登入 Django Admin：")
    print("  網址: http://127.0.0.1:8000/panel/system-admin/")
    print()
    print("提示：請記住您的密碼，系統不會顯示明文密碼")
    print()

except Exception as e:
    print()
    print("=" * 60)
    print("[錯誤] 建立超級使用者失敗")
    print("=" * 60)
    print(f"\n錯誤訊息: {e}")
    print()
