# -*- coding: utf-8 -*-
"""
JSON格式化和語法高亮模組
功能：提供JSON語法檢查、格式化和高亮顯示
"""

import json
import re
import tkinter as tk
from tkinter import font
from typing import Dict, List, Tuple, Optional


class JSONFormatter:
    """JSON格式化器"""
    
    def __init__(self):
        self.indent_size = 2
        
    def validate_json(self, json_str: str) -> Tuple[bool, str, Optional[dict]]:
        """驗證JSON格式"""
        if not json_str.strip():
            return True, "空內容", {}
            
        try:
            parsed = json.loads(json_str)
            return True, "JSON格式正確", parsed
        except json.JSONDecodeError as e:
            error_msg = self._format_json_error(json_str, e)
            return False, error_msg, None
        except Exception as e:
            return False, f"解析錯誤: {str(e)}", None
    
    def _format_json_error(self, json_str: str, error: json.JSONDecodeError) -> str:
        """格式化JSON錯誤訊息"""
        lines = json_str.split('\n')
        error_line_num = error.lineno
        error_col_num = error.colno
        
        error_details = []
        error_details.append(f"JSON語法錯誤:")
        error_details.append(f"  錯誤訊息: {error.msg}")
        error_details.append(f"  位置: 第 {error_line_num} 行，第 {error_col_num} 列")
        
        # 顯示錯誤行的上下文
        start_line = max(0, error_line_num - 3)
        end_line = min(len(lines), error_line_num + 2)
        
        error_details.append(f"\n錯誤上下文:")
        for i in range(start_line, end_line):
            line_num = i + 1
            line_content = lines[i] if i < len(lines) else ""
            
            if line_num == error_line_num:
                # 標記錯誤行
                error_details.append(f"→ {line_num:3d}: {line_content}")
                # 添加錯誤位置指示
                if error_col_num <= len(line_content):
                    pointer = " " * (6 + error_col_num - 1) + "^"
                    error_details.append(pointer)
            else:
                error_details.append(f"  {line_num:3d}: {line_content}")
        
        return '\n'.join(error_details)
    
    def format_json(self, json_str: str, indent: int = None) -> str:
        """格式化JSON字符串"""
        if indent is None:
            indent = self.indent_size
            
        try:
            parsed = json.loads(json_str)
            return json.dumps(parsed, indent=indent, ensure_ascii=False, sort_keys=True)
        except:
            return json_str
    
    def minify_json(self, json_str: str) -> str:
        """壓縮JSON字符串"""
        try:
            parsed = json.loads(json_str)
            return json.dumps(parsed, separators=(',', ':'), ensure_ascii=False)
        except:
            return json_str
    
    def get_json_info(self, json_str: str) -> Dict[str, any]:
        """獲取JSON資訊"""
        try:
            parsed = json.loads(json_str)
            
            def count_elements(obj, counts=None):
                if counts is None:
                    counts = {'objects': 0, 'arrays': 0, 'strings': 0, 
                             'numbers': 0, 'booleans': 0, 'nulls': 0}
                
                if isinstance(obj, dict):
                    counts['objects'] += 1
                    for value in obj.values():
                        count_elements(value, counts)
                elif isinstance(obj, list):
                    counts['arrays'] += 1
                    for item in obj:
                        count_elements(item, counts)
                elif isinstance(obj, str):
                    counts['strings'] += 1
                elif isinstance(obj, (int, float)):
                    counts['numbers'] += 1
                elif isinstance(obj, bool):
                    counts['booleans'] += 1
                elif obj is None:
                    counts['nulls'] += 1
                
                return counts
            
            element_counts = count_elements(parsed)
            
            return {
                'valid': True,
                'size_bytes': len(json_str.encode('utf-8')),
                'size_chars': len(json_str),
                'lines': len(json_str.split('\n')),
                'type': type(parsed).__name__,
                'elements': element_counts
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'size_bytes': len(json_str.encode('utf-8')),
                'size_chars': len(json_str),
                'lines': len(json_str.split('\n'))
            }


class JSONSyntaxHighlighter:
    """JSON語法高亮器（用於tkinter Text widget）"""
    
    def __init__(self, text_widget: tk.Text):
        self.text_widget = text_widget
        self.setup_tags()
    
    def setup_tags(self):
        """設置語法高亮標籤"""
        # 定義顏色方案
        self.text_widget.tag_configure("json_key", foreground="#0066CC", font=("Consolas", 10, "bold"))
        self.text_widget.tag_configure("json_string", foreground="#008000")
        self.text_widget.tag_configure("json_number", foreground="#FF6600")
        self.text_widget.tag_configure("json_boolean", foreground="#0000FF", font=("Consolas", 10, "bold"))
        self.text_widget.tag_configure("json_null", foreground="#808080", font=("Consolas", 10, "bold"))
        self.text_widget.tag_configure("json_bracket", foreground="#000000", font=("Consolas", 10, "bold"))
        self.text_widget.tag_configure("json_error", background="#FFE6E6", foreground="#CC0000")
        self.text_widget.tag_configure("json_comment", foreground="#808080", font=("Consolas", 10, "italic"))
    
    def highlight_json(self, start_index="1.0", end_index="end"):
        """對JSON文本進行語法高亮"""
        # 清除現有標籤
        for tag in ["json_key", "json_string", "json_number", "json_boolean", 
                   "json_null", "json_bracket", "json_error"]:
            self.text_widget.tag_remove(tag, start_index, end_index)
        
        content = self.text_widget.get(start_index, end_index)
        
        # JSON語法正則表達式
        patterns = [
            (r'"[^"\\]*(?:\\.[^"\\]*)*"\s*:', "json_key"),      # JSON鍵
            (r'"[^"\\]*(?:\\.[^"\\]*)*"', "json_string"),       # 字符串值
            (r'-?\d+\.?\d*([eE][+-]?\d+)?', "json_number"),     # 數字
            (r'\b(true|false)\b', "json_boolean"),              # 布爾值
            (r'\bnull\b', "json_null"),                         # null值
            (r'[{}\[\],:]', "json_bracket"),                    # 括號和分隔符
        ]
        
        for pattern, tag in patterns:
            for match in re.finditer(pattern, content):
                start_pos = f"{start_index.split('.')[0]}.{int(start_index.split('.')[1]) + match.start()}"
                end_pos = f"{start_index.split('.')[0]}.{int(start_index.split('.')[1]) + match.end()}"
                self.text_widget.tag_add(tag, start_pos, end_pos)
    
    def highlight_errors(self, json_str: str):
        """高亮JSON錯誤"""
        try:
            json.loads(json_str)
            # JSON有效，移除錯誤標籤
            self.text_widget.tag_remove("json_error", "1.0", "end")
        except json.JSONDecodeError as e:
            # 標記錯誤位置
            lines = json_str.split('\n')
            if e.lineno <= len(lines):
                error_line = e.lineno
                error_col = e.colno
                
                # 計算錯誤位置
                start_pos = f"{error_line}.{max(0, error_col - 1)}"
                end_pos = f"{error_line}.{min(len(lines[error_line - 1]), error_col + 5)}"
                
                self.text_widget.tag_add("json_error", start_pos, end_pos)


class JSONValidator:
    """JSON驗證器"""
    
    @staticmethod
    def validate_and_format(json_str: str) -> Dict[str, any]:
        """驗證並格式化JSON"""
        formatter = JSONFormatter()
        
        # 驗證JSON
        is_valid, message, parsed = formatter.validate_json(json_str)
        
        result = {
            'valid': is_valid,
            'message': message,
            'parsed': parsed
        }
        
        if is_valid and parsed is not None:
            # 格式化JSON
            result['formatted'] = formatter.format_json(json_str)
            result['minified'] = formatter.minify_json(json_str)
            result['info'] = formatter.get_json_info(json_str)
        
        return result
    
    @staticmethod
    def get_common_json_templates() -> Dict[str, str]:
        """獲取常用JSON模板"""
        return {
            "空物件": "{}",
            "空陣列": "[]",
            "基本物件": '''{
  "name": "example",
  "value": 123,
  "active": true,
  "data": null
}''',
            "陣列範例": '''[
  {
    "id": 1,
    "name": "項目1"
  },
  {
    "id": 2,
    "name": "項目2"
  }
]''',
            "API請求範例": '''{
  "method": "POST",
  "url": "https://api.example.com/data",
  "headers": {
    "Content-Type": "application/json",
    "Authorization": "Bearer token"
  },
  "body": {
    "user": "example",
    "action": "create"
  }
}'''
        }


if __name__ == "__main__":
    # 測試代碼
    formatter = JSONFormatter()
    
    # 測試有效JSON
    valid_json = '{"name": "test", "value": 123, "active": true}'
    is_valid, msg, parsed = formatter.validate_json(valid_json)
    print(f"有效JSON: {is_valid}, 訊息: {msg}")
    
    # 測試無效JSON
    invalid_json = '{"name": "test", "value": 123, "active": true'
    is_valid, msg, parsed = formatter.validate_json(invalid_json)
    print(f"無效JSON: {is_valid}")
    print(f"錯誤訊息:\n{msg}")
