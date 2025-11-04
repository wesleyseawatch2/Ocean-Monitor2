"""
Django 專案虛擬環境快速設置
支援 Windows/macOS/Linux
"""
import os
import sys
import subprocess
from pathlib import Path


def run_command(cmd, shell=False):
    """執行命令"""
    try:
        result = subprocess.run(cmd, shell=shell, check=True, text=True, 
                              capture_output=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr


def create_venv():
    """建立虛擬環境"""
    print("📦 建立虛擬環境...")
    
    venv_path = Path('venv')
    if venv_path.exists():
        print("  ⚠️  虛擬環境已存在，跳過建立")
        return True
    
    success, output = run_command([sys.executable, '-m', 'venv', 'venv'])
    if success:
        print("  ✓ 虛擬環境建立成功")
        return True
    else:
        print(f"  ✗ 建立失敗: {output}")
        return False


def get_pip_path():
    """取得 pip 路徑"""
    if sys.platform == 'win32':
        return Path('venv/Scripts/pip.exe')
    else:
        return Path('venv/bin/pip')


def install_packages():
    """安裝套件"""
    print("\n📥 安裝 Django 和相關套件...")
    
    pip_path = get_pip_path()
    
    packages = [
        'django>=4.2',
        'pillow',  # 圖片處理
        'python-decouple',  # 環境變數管理
    ]
    
    for package in packages:
        print(f"  安裝 {package}...")
        success, _ = run_command([str(pip_path), 'install', package])
        if success:
            print(f"    ✓ {package}")
        else:
            print(f"    ✗ {package} 安裝失敗")
    
    return True


def create_requirements():
    """建立 requirements.txt"""
    print("\n📝 建立 requirements.txt...")
    
    pip_path = get_pip_path()
    success, output = run_command([str(pip_path), 'freeze'])
    
    if success:
        with open('requirements.txt', 'w', encoding='utf-8') as f:
            f.write(output)
        print("  ✓ requirements.txt 建立成功")
    else:
        print("  ✗ 建立失敗")


def create_gitignore():
    """建立 .gitignore"""
    print("\n📄 建立 .gitignore...")
    
    gitignore_content = """# Python
*.py[cod]
*$py.class
__pycache__/
*.so

# Virtual Environment
venv/
env/
ENV/

# Django
*.log
db.sqlite3
db.sqlite3-journal
/media
/staticfiles

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Environment
.env
.env.local
"""
    
    with open('.gitignore', 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    
    print("  ✓ .gitignore 建立成功")


def create_env_example():
    """建立 .env.example"""
    print("\n🔐 建立 .env.example...")
    
    env_content = """# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=ocean_monitor
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
"""
    
    with open('.env.example', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("  ✓ .env.example 建立成功")


def show_activation_instructions():
    """顯示啟動指令"""
    print("\n" + "="*60)
    print("✅ 虛擬環境設置完成！")
    print("="*60)
    
    if sys.platform == 'win32':
        activate_cmd = "venv\\Scripts\\activate"
    else:
        activate_cmd = "source venv/bin/activate"
    
    print(f"\n📌 啟動虛擬環境:")
    print(f"   {activate_cmd}")
    print(f"\n📌 停用虛擬環境:")
    print(f"   deactivate")
    print(f"\n📌 安裝依賴套件 (其他電腦):")
    print(f"   pip install -r requirements.txt")
    print(f"\n📌 啟動 Django 專案:")
    print(f"   python manage.py runserver")
    print()


def main():
    """主程序"""
    print("🚀 Django 專案虛擬環境設置")
    print("="*60)
    
    # 檢查是否在專案目錄
    if not Path('manage.py').exists():
        print("⚠️  請在 Django 專案根目錄執行此腳本")
        print("   (需要有 manage.py 的目錄)")
        sys.exit(1)
    
    # 執行設置步驟
    if not create_venv():
        sys.exit(1)
    
    install_packages()
    create_requirements()
    create_gitignore()
    create_env_example()
    show_activation_instructions()


if __name__ == '__main__':
    main()