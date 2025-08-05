#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DHCP Finder 模組測試腳本
用於測試各個功能模組是否正常工作
"""

import sys
import traceback
from modules.network_info import NetworkInfo
from modules.internet_test import InternetTest
from modules.dhcp_scanner import DHCPScanner


def test_network_info():
    """測試網路資訊模組"""
    print("=" * 50)
    print("測試網路資訊模組...")
    try:
        network_info = NetworkInfo()
        interfaces = network_info.get_network_interfaces()
        
        print(f"找到 {len(interfaces)} 個網路介面:")
        for i, interface in enumerate(interfaces[:3]):  # 只顯示前3個
            print(f"  {i+1}. {interface['name']} - {interface['status']}")
            if 'ip' in interface:
                print(f"     IP: {interface['ip']}")
            if 'mac' in interface:
                print(f"     MAC: {interface['mac']}")
                
        print("✓ 網路資訊模組測試通過")
        return True
        
    except Exception as e:
        print(f"✗ 網路資訊模組測試失敗: {e}")
        traceback.print_exc()
        return False


def test_internet_connectivity():
    """測試外網連線模組"""
    print("=" * 50)
    print("測試外網連線模組...")
    try:
        internet_test = InternetTest()
        
        # 測試基本連線
        print("測試基本連線...")
        result = internet_test.test_connectivity()
        
        if result['connected']:
            print("✓ 外網連線正常")
            if result.get('ping'):
                print(f"  平均延遲: {result['ping']:.2f} ms")
        else:
            print("⚠ 外網連線異常")
            
        # 測試公網IP獲取
        print("測試公網IP獲取...")
        public_ip = internet_test.get_public_ip()
        if public_ip:
            print(f"✓ 公網IP: {public_ip}")
        else:
            print("⚠ 無法獲取公網IP")
            
        print("✓ 外網連線模組測試通過")
        return True
        
    except Exception as e:
        print(f"✗ 外網連線模組測試失敗: {e}")
        traceback.print_exc()
        return False


def test_dhcp_scanner():
    """測試DHCP掃描模組"""
    print("=" * 50)
    print("測試DHCP掃描模組...")
    try:
        dhcp_scanner = DHCPScanner()
        
        print("執行DHCP掃描（這可能需要幾秒鐘）...")
        servers = dhcp_scanner.scan_dhcp_servers()
        
        if servers:
            print(f"✓ 找到 {len(servers)} 個DHCP伺服器:")
            for server in servers:
                print(f"  IP: {server['ip']}")
                print(f"  MAC: {server['mac']}")
                print(f"  廠商: {server.get('vendor', '未知')}")
                print("-" * 30)
        else:
            print("⚠ 未找到DHCP伺服器（這可能是正常的）")
            
        print("✓ DHCP掃描模組測試通過")
        return True
        
    except Exception as e:
        print(f"✗ DHCP掃描模組測試失敗: {e}")
        traceback.print_exc()
        return False


def test_speed_test():
    """測試網速測試模組"""
    print("=" * 50)
    print("測試網速測試模組...")
    try:
        internet_test = InternetTest()
        
        print("執行網速測試（這可能需要較長時間）...")
        print("注意：如果網路較慢或不穩定，此測試可能會失敗")
        
        result = internet_test.test_speed()
        
        if result['success']:
            print("✓ 網速測試成功:")
            print(f"  下載速度: {result['download']:.2f} Mbps")
            print(f"  上傳速度: {result['upload']:.2f} Mbps")
            print(f"  延遲: {result['ping']:.2f} ms")
        else:
            print(f"⚠ 網速測試失敗: {result.get('error', '未知錯誤')}")
            
        print("✓ 網速測試模組測試通過")
        return True
        
    except Exception as e:
        print(f"✗ 網速測試模組測試失敗: {e}")
        traceback.print_exc()
        return False


def main():
    """主測試函數"""
    print("DHCP Finder 模組測試")
    print("=" * 50)
    
    tests = [
        ("網路資訊", test_network_info),
        ("外網連線", test_internet_connectivity),
        ("DHCP掃描", test_dhcp_scanner),
    ]
    
    # 詢問是否執行網速測試
    try:
        speed_test_choice = input("是否執行網速測試？(y/n，預設n): ").lower()
        if speed_test_choice == 'y':
            tests.append(("網速測試", test_speed_test))
    except (EOFError, KeyboardInterrupt):
        print("\n跳過網速測試")
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n開始測試: {test_name}")
        try:
            if test_func():
                passed += 1
        except KeyboardInterrupt:
            print(f"\n用戶中斷了 {test_name} 測試")
            break
        except Exception as e:
            print(f"測試 {test_name} 時發生未預期的錯誤: {e}")
    
    print("\n" + "=" * 50)
    print("測試結果總結:")
    print(f"通過: {passed}/{total}")
    
    if passed == total:
        print("✓ 所有測試都通過了！")
        return 0
    else:
        print("⚠ 部分測試失敗，請檢查錯誤訊息")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n測試被用戶中斷")
        sys.exit(1)
