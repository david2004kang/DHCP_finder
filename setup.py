#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DHCP Finder 安裝腳本
用於自動安裝依賴套件和設定環境
"""

import subprocess
import sys
import os
import platform


def check_python_version():
    """檢查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("錯誤: 需要Python 3.8或更高版本")
        print(f"目前版本: {version.major}.{version.minor}.{version.micro}")
        return False
    return True


def install_requirements():
    """安裝依賴套件"""
    print("正在安裝依賴套件...")
    
    try:
        # 升級pip
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # 安裝requirements.txt中的套件
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        print("依賴套件安裝完成！")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"安裝依賴套件失敗: {e}")
        return False


def check_admin_rights():
    """檢查是否有管理員權限"""
    try:
        if platform.system() == "Windows":
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        else:
            return os.geteuid() == 0
    except:
        return False


def create_desktop_shortcut():
    """創建桌面捷徑（Windows）"""
    if platform.system() != "Windows":
        return
        
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        path = os.path.join(desktop, "DHCP Finder.lnk")
        target = os.path.join(os.getcwd(), "main.py")
        wDir = os.getcwd()
        icon = target
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = sys.executable
        shortcut.Arguments = f'"{target}"'
        shortcut.WorkingDirectory = wDir
        shortcut.IconLocation = icon
        shortcut.save()
        
        print("桌面捷徑創建成功！")
        
    except ImportError:
        print("無法創建桌面捷徑（缺少winshell或pywin32）")
    except Exception as e:
        print(f"創建桌面捷徑失敗: {e}")


def main():
    """主函數"""
    print("=" * 50)
    print("DHCP Finder 安裝程式")
    print("=" * 50)
    
    # 檢查Python版本
    if not check_python_version():
        input("按Enter鍵結束...")
        return
    
    print(f"Python版本: {sys.version}")
    print(f"作業系統: {platform.system()} {platform.release()}")
    
    # 檢查管理員權限
    if check_admin_rights():
        print("✓ 以管理員身份執行")
    else:
        print("⚠ 未以管理員身份執行，某些功能可能受限")
    
    # 安裝依賴套件
    if not install_requirements():
        input("按Enter鍵結束...")
        return
    
    # 詢問是否創建桌面捷徑
    if platform.system() == "Windows":
        choice = input("是否創建桌面捷徑? (y/n): ").lower()
        if choice == 'y':
            create_desktop_shortcut()
    
    print("\n" + "=" * 50)
    print("安裝完成！")
    print("=" * 50)
    print("\n使用方法:")
    print("1. 直接執行: python main.py")
    print("2. 編譯成exe: 執行 build.bat")
    print("3. 除錯版本: 執行 build_debug.bat")
    print("\n注意事項:")
    print("- 建議以管理員身份執行以獲得完整功能")
    print("- 防火牆可能會詢問網路存取權限，請允許")
    
    input("\n按Enter鍵結束...")


if __name__ == "__main__":
    main()
