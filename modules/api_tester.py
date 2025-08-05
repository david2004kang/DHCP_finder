# -*- coding: utf-8 -*-
"""
API測試模組
功能：提供HTTP請求測試功能，支援GET/POST方法
"""

import json
import requests
import time
from urllib.parse import urlparse
from typing import Dict, Any, Optional, Tuple


class APITester:
    """API測試器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.timeout = 30
        self.max_redirects = 5
        
    def validate_url(self, url: str) -> Tuple[bool, str]:
        """驗證URL格式"""
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                return False, "URL格式不正確，需要包含協議（http://或https://）"
            if result.scheme not in ['http', 'https']:
                return False, "只支援HTTP和HTTPS協議"
            return True, ""
        except Exception as e:
            return False, f"URL解析錯誤: {str(e)}"
    
    def validate_json(self, json_str: str) -> Tuple[bool, str, Optional[Dict]]:
        """驗證JSON格式"""
        if not json_str.strip():
            return True, "", {}
            
        try:
            parsed = json.loads(json_str)
            return True, "JSON格式正確", parsed
        except json.JSONDecodeError as e:
            error_msg = f"JSON格式錯誤 (行 {e.lineno}, 列 {e.colno}): {e.msg}"
            return False, error_msg, None
        except Exception as e:
            return False, f"JSON解析錯誤: {str(e)}", None
    
    def format_json(self, json_str: str, indent: int = 2) -> str:
        """格式化JSON字符串"""
        try:
            parsed = json.loads(json_str)
            return json.dumps(parsed, indent=indent, ensure_ascii=False, sort_keys=True)
        except:
            return json_str
    
    def prepare_headers(self, headers_text: str) -> Dict[str, str]:
        """解析headers文本"""
        headers = {}
        if not headers_text.strip():
            return headers
            
        for line in headers_text.strip().split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip()] = value.strip()
        
        return headers
    
    def send_request(self, method: str, url: str, headers: Dict[str, str] = None, 
                    data: str = None, params: Dict[str, str] = None) -> Dict[str, Any]:
        """發送HTTP請求"""
        start_time = time.time()
        
        try:
            # 驗證URL
            is_valid, error_msg = self.validate_url(url)
            if not is_valid:
                return {
                    'success': False,
                    'error': error_msg,
                    'status_code': None,
                    'response_time': 0,
                    'headers': {},
                    'content': ''
                }
            
            # 準備請求參數
            request_kwargs = {
                'timeout': self.timeout,
                'allow_redirects': True
            }
            
            if headers:
                request_kwargs['headers'] = headers
            
            if params:
                request_kwargs['params'] = params
            
            # 處理請求體
            if data and method.upper() in ['POST', 'PUT', 'PATCH']:
                # 檢查是否為JSON
                if headers and any('json' in str(v).lower() for v in headers.values()):
                    try:
                        request_kwargs['json'] = json.loads(data)
                    except json.JSONDecodeError:
                        request_kwargs['data'] = data
                else:
                    request_kwargs['data'] = data
            
            # 發送請求
            response = self.session.request(method.upper(), url, **request_kwargs)
            end_time = time.time()
            
            # 處理響應
            try:
                # 嘗試解析JSON響應
                if 'json' in response.headers.get('content-type', '').lower():
                    content = response.json()
                    formatted_content = json.dumps(content, indent=2, ensure_ascii=False)
                else:
                    content = response.text
                    formatted_content = content
            except:
                content = response.text
                formatted_content = content
            
            return {
                'success': True,
                'status_code': response.status_code,
                'status_text': response.reason,
                'response_time': round((end_time - start_time) * 1000, 2),
                'headers': dict(response.headers),
                'content': content,
                'formatted_content': formatted_content,
                'url': response.url,
                'encoding': response.encoding,
                'size': len(response.content)
            }
            
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': f'請求超時（{self.timeout}秒）',
                'status_code': None,
                'response_time': round((time.time() - start_time) * 1000, 2),
                'headers': {},
                'content': ''
            }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': '連線錯誤，無法連接到伺服器',
                'status_code': None,
                'response_time': round((time.time() - start_time) * 1000, 2),
                'headers': {},
                'content': ''
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'請求錯誤: {str(e)}',
                'status_code': None,
                'response_time': round((time.time() - start_time) * 1000, 2),
                'headers': {},
                'content': ''
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'未知錯誤: {str(e)}',
                'status_code': None,
                'response_time': round((time.time() - start_time) * 1000, 2),
                'headers': {},
                'content': ''
            }
    
    def get_request(self, url: str, headers: Dict[str, str] = None, 
                   params: Dict[str, str] = None) -> Dict[str, Any]:
        """發送GET請求"""
        return self.send_request('GET', url, headers, None, params)
    
    def post_request(self, url: str, headers: Dict[str, str] = None, 
                    data: str = None, params: Dict[str, str] = None) -> Dict[str, Any]:
        """發送POST請求"""
        return self.send_request('POST', url, headers, data, params)
    
    def put_request(self, url: str, headers: Dict[str, str] = None, 
                   data: str = None, params: Dict[str, str] = None) -> Dict[str, Any]:
        """發送PUT請求"""
        return self.send_request('PUT', url, headers, data, params)
    
    def delete_request(self, url: str, headers: Dict[str, str] = None, 
                      params: Dict[str, str] = None) -> Dict[str, Any]:
        """發送DELETE請求"""
        return self.send_request('DELETE', url, headers, None, params)


class JSONHighlighter:
    """JSON語法高亮器"""
    
    @staticmethod
    def highlight_json_errors(json_str: str) -> str:
        """高亮JSON錯誤"""
        try:
            json.loads(json_str)
            return "JSON格式正確 ✓"
        except json.JSONDecodeError as e:
            lines = json_str.split('\n')
            error_line = e.lineno - 1
            error_col = e.colno - 1
            
            result = []
            for i, line in enumerate(lines):
                if i == error_line:
                    # 標記錯誤位置
                    if error_col < len(line):
                        marked_line = (line[:error_col] + 
                                     f"[ERROR→]{line[error_col]}" + 
                                     f"[←ERROR]" + line[error_col + 1:])
                    else:
                        marked_line = line + " [ERROR→缺少字符←ERROR]"
                    result.append(f"第{i+1}行: {marked_line}")
                else:
                    result.append(f"第{i+1}行: {line}")
            
            error_info = f"\n錯誤詳情: {e.msg} (行 {e.lineno}, 列 {e.colno})"
            return '\n'.join(result) + error_info
        except Exception as e:
            return f"JSON解析錯誤: {str(e)}"


if __name__ == "__main__":
    # 測試代碼
    tester = APITester()
    
    # 測試GET請求
    print("測試GET請求...")
    result = tester.get_request("https://httpbin.org/get")
    if result['success']:
        print(f"狀態碼: {result['status_code']}")
        print(f"響應時間: {result['response_time']}ms")
    else:
        print(f"錯誤: {result['error']}")
    
    # 測試JSON驗證
    print("\n測試JSON驗證...")
    test_json = '{"name": "test", "value": 123}'
    is_valid, msg, parsed = tester.validate_json(test_json)
    print(f"JSON有效: {is_valid}, 訊息: {msg}")
