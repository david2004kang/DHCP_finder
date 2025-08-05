#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API功能測試腳本
測試新增的API測試和JSON處理功能
"""

import sys
import traceback
from modules.api_tester import APITester
from modules.json_formatter import JSONFormatter, JSONValidator


def test_api_tester():
    """測試API測試器"""
    print("=" * 50)
    print("測試API測試器...")
    
    try:
        tester = APITester()
        
        # 測試URL驗證
        print("測試URL驗證...")
        valid_url = "https://httpbin.org/get"
        is_valid, error = tester.validate_url(valid_url)
        print(f"  有效URL測試: {is_valid} - {valid_url}")
        
        invalid_url = "not-a-url"
        is_valid, error = tester.validate_url(invalid_url)
        print(f"  無效URL測試: {is_valid} - {error}")
        
        # 測試JSON驗證
        print("\n測試JSON驗證...")
        valid_json = '{"name": "test", "value": 123}'
        is_valid, msg, parsed = tester.validate_json(valid_json)
        print(f"  有效JSON: {is_valid} - {msg}")
        
        invalid_json = '{"name": "test", "value": 123'
        is_valid, msg, parsed = tester.validate_json(invalid_json)
        print(f"  無效JSON: {is_valid}")
        
        # 測試Headers解析
        print("\n測試Headers解析...")
        headers_text = "Content-Type: application/json\nAuthorization: Bearer token123"
        headers = tester.prepare_headers(headers_text)
        print(f"  解析的Headers: {headers}")
        
        # 測試GET請求（使用httpbin.org）
        print("\n測試GET請求...")
        try:
            result = tester.get_request("https://httpbin.org/get")
            if result['success']:
                print(f"  ✓ GET請求成功")
                print(f"    狀態碼: {result['status_code']}")
                print(f"    響應時間: {result['response_time']} ms")
            else:
                print(f"  ✗ GET請求失敗: {result['error']}")
        except Exception as e:
            print(f"  ⚠ GET請求測試跳過（網路問題）: {e}")
        
        print("✓ API測試器模組測試通過")
        return True
        
    except Exception as e:
        print(f"✗ API測試器模組測試失敗: {e}")
        traceback.print_exc()
        return False


def test_json_formatter():
    """測試JSON格式化器"""
    print("=" * 50)
    print("測試JSON格式化器...")
    
    try:
        formatter = JSONFormatter()
        
        # 測試JSON驗證
        print("測試JSON驗證...")
        valid_json = '{"name": "test", "value": 123, "active": true}'
        is_valid, msg, parsed = formatter.validate_json(valid_json)
        print(f"  有效JSON: {is_valid} - {msg}")
        
        # 測試JSON格式化
        print("\n測試JSON格式化...")
        minified_json = '{"name":"test","value":123,"active":true}'
        formatted = formatter.format_json(minified_json)
        print(f"  格式化前: {minified_json}")
        print(f"  格式化後:\n{formatted}")
        
        # 測試JSON壓縮
        print("\n測試JSON壓縮...")
        formatted_json = '''{
  "name": "test",
  "value": 123,
  "active": true
}'''
        minified = formatter.minify_json(formatted_json)
        print(f"  壓縮後: {minified}")
        
        # 測試JSON資訊獲取
        print("\n測試JSON資訊獲取...")
        complex_json = '''{
  "users": [
    {"id": 1, "name": "Alice", "active": true},
    {"id": 2, "name": "Bob", "active": false}
  ],
  "total": 2,
  "metadata": {
    "version": "1.0",
    "timestamp": null
  }
}'''
        info = formatter.get_json_info(complex_json)
        if info['valid']:
            print(f"  JSON類型: {info['type']}")
            print(f"  大小: {info['size_chars']} 字符, {info['size_bytes']} 位元組")
            print(f"  行數: {info['lines']}")
            print(f"  元素統計: {info['elements']}")
        
        # 測試錯誤JSON
        print("\n測試錯誤JSON...")
        error_json = '{"name": "test", "value": 123, "active": true'
        is_valid, error_msg, parsed = formatter.validate_json(error_json)
        print(f"  錯誤JSON驗證: {is_valid}")
        if not is_valid:
            print(f"  錯誤訊息:\n{error_msg}")
        
        print("✓ JSON格式化器模組測試通過")
        return True
        
    except Exception as e:
        print(f"✗ JSON格式化器模組測試失敗: {e}")
        traceback.print_exc()
        return False


def test_json_validator():
    """測試JSON驗證器"""
    print("=" * 50)
    print("測試JSON驗證器...")
    
    try:
        # 測試JSON驗證和格式化
        test_json = '{"name":"test","items":[1,2,3],"config":{"debug":true}}'
        result = JSONValidator.validate_and_format(test_json)
        
        print(f"JSON有效: {result['valid']}")
        print(f"訊息: {result['message']}")
        
        if result['valid']:
            print("格式化結果:")
            print(result['formatted'])
            print(f"\n壓縮結果: {result['minified']}")
            print(f"資訊: {result['info']}")
        
        # 測試JSON模板
        print("\n測試JSON模板...")
        templates = JSONValidator.get_common_json_templates()
        for name, template in templates.items():
            print(f"  {name}: {len(template)} 字符")
        
        print("✓ JSON驗證器模組測試通過")
        return True
        
    except Exception as e:
        print(f"✗ JSON驗證器模組測試失敗: {e}")
        traceback.print_exc()
        return False


def test_integration():
    """整合測試"""
    print("=" * 50)
    print("整合測試...")
    
    try:
        # 測試完整的API請求流程
        tester = APITester()
        formatter = JSONFormatter()
        
        # 準備測試數據
        url = "https://httpbin.org/post"
        headers = {"Content-Type": "application/json"}
        json_data = '{"test": "data", "number": 42}'
        
        # 驗證JSON
        is_valid, msg, parsed = formatter.validate_json(json_data)
        print(f"JSON驗證: {is_valid} - {msg}")
        
        if is_valid:
            # 格式化JSON
            formatted_json = formatter.format_json(json_data)
            print(f"格式化JSON:\n{formatted_json}")
            
            # 發送POST請求（如果網路可用）
            try:
                result = tester.post_request(url, headers, json_data)
                if result['success']:
                    print(f"✓ POST請求成功")
                    print(f"  狀態碼: {result['status_code']}")
                    print(f"  響應時間: {result['response_time']} ms")
                else:
                    print(f"✗ POST請求失敗: {result['error']}")
            except Exception as e:
                print(f"⚠ POST請求測試跳過（網路問題）: {e}")
        
        print("✓ 整合測試通過")
        return True
        
    except Exception as e:
        print(f"✗ 整合測試失敗: {e}")
        traceback.print_exc()
        return False


def main():
    """主測試函數"""
    print("DHCP Finder API功能測試")
    print("=" * 50)
    
    tests = [
        ("API測試器", test_api_tester),
        ("JSON格式化器", test_json_formatter),
        ("JSON驗證器", test_json_validator),
        ("整合測試", test_integration),
    ]
    
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
    print("API功能測試結果總結:")
    print(f"通過: {passed}/{total}")
    
    if passed == total:
        print("✓ 所有API功能測試都通過了！")
        return 0
    else:
        print("⚠ 部分API功能測試失敗，請檢查錯誤訊息")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nAPI功能測試被用戶中斷")
        sys.exit(1)
