#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DHCP Finder - 網路工具主程式
功能：
1. DHCP伺服器掃描
2. 網路介面卡資訊
3. 外網連線及網速測試
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import sys
import os

# 導入功能模組
from modules.dhcp_scanner import DHCPScanner
from modules.network_info import NetworkInfo
from modules.internet_test import InternetTest
from modules.api_tester import APITester
from modules.json_formatter import JSONFormatter, JSONSyntaxHighlighter, JSONValidator


class DHCPFinderGUI:
    """DHCP Finder 主要GUI類別"""

    def __init__(self, root):
        self.root = root
        self.root.title("DHCP Finder - 網路工具 v1.1")
        self.root.geometry("900x700")
        self.root.resizable(True, True)

        # 初始化功能模組
        self.dhcp_scanner = DHCPScanner()
        self.network_info = NetworkInfo()
        self.internet_test = InternetTest()
        self.api_tester = APITester()
        self.json_formatter = JSONFormatter()

        # 頁面管理
        self.current_page = "network"  # 預設頁面
        self.pages = {}

        self.setup_ui()

    def setup_ui(self):
        """設置使用者介面"""
        # 創建主要框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置網格權重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # 標題
        title_label = ttk.Label(main_frame, text="DHCP Finder - 網路診斷工具",
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 10))

        # 頁面切換按鈕
        tab_frame = ttk.Frame(main_frame)
        tab_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Button(tab_frame, text="網路診斷", command=lambda: self.switch_page("network"),
                  width=15).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(tab_frame, text="API測試", command=lambda: self.switch_page("api"),
                  width=15).pack(side=tk.LEFT, padx=5)

        # 頁面容器
        self.page_container = ttk.Frame(main_frame)
        self.page_container.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.page_container.columnconfigure(0, weight=1)
        self.page_container.rowconfigure(0, weight=1)

        # 創建頁面
        self.create_network_page()
        self.create_api_page()

        # 顯示預設頁面
        self.switch_page("network")

    def switch_page(self, page_name):
        """切換頁面"""
        # 隱藏所有頁面
        for page in self.pages.values():
            page.grid_remove()

        # 顯示指定頁面
        if page_name in self.pages:
            self.pages[page_name].grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            self.current_page = page_name

    def create_network_page(self):
        """創建網路診斷頁面"""
        network_frame = ttk.Frame(self.page_container)
        network_frame.columnconfigure(1, weight=1)
        network_frame.rowconfigure(0, weight=1)

        # 左側按鈕面板
        button_frame = ttk.LabelFrame(network_frame, text="功能選單", padding="10")
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

        # 功能按鈕
        ttk.Button(button_frame, text="掃描DHCP伺服器",
                  command=self.scan_dhcp_servers, width=20).pack(pady=5, fill=tk.X)

        ttk.Button(button_frame, text="網路介面卡資訊",
                  command=self.show_network_info, width=20).pack(pady=5, fill=tk.X)

        ttk.Button(button_frame, text="外網連線測試",
                  command=self.test_internet, width=20).pack(pady=5, fill=tk.X)

        ttk.Button(button_frame, text="網速測試",
                  command=self.test_speed, width=20).pack(pady=5, fill=tk.X)

        ttk.Separator(button_frame, orient='horizontal').pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="清除結果",
                  command=self.clear_results, width=20).pack(pady=5, fill=tk.X)

        ttk.Button(button_frame, text="關於",
                  command=self.show_about, width=20).pack(pady=5, fill=tk.X)

        # 右側結果顯示區域
        result_frame = ttk.LabelFrame(network_frame, text="結果顯示", padding="10")
        result_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)

        # 結果文字區域
        self.result_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD,
                                                    width=50, height=25)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 狀態列
        status_frame = ttk.Frame(network_frame)
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.columnconfigure(0, weight=1)

        self.status_var = tk.StringVar()
        self.status_var.set("就緒")
        status_bar = ttk.Label(status_frame, textvariable=self.status_var,
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=0, column=0, sticky=(tk.W, tk.E))

        self.pages["network"] = network_frame

    def create_api_page(self):
        """創建API測試頁面"""
        api_frame = ttk.Frame(self.page_container)
        api_frame.columnconfigure(0, weight=1)
        api_frame.rowconfigure(1, weight=1)

        # 上方控制面板
        control_frame = ttk.LabelFrame(api_frame, text="API請求設定", padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        control_frame.columnconfigure(1, weight=1)

        # HTTP方法選擇
        ttk.Label(control_frame, text="方法:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.method_var = tk.StringVar(value="GET")
        method_combo = ttk.Combobox(control_frame, textvariable=self.method_var,
                                   values=["GET", "POST", "PUT", "DELETE"], width=10, state="readonly")
        method_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))

        # URL輸入
        ttk.Label(control_frame, text="URL:").grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(control_frame, textvariable=self.url_var, width=50)
        url_entry.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(0, 10))

        # 發送按鈕
        ttk.Button(control_frame, text="發送請求", command=self.send_api_request,
                  width=12).grid(row=0, column=4, padx=(10, 0))

        # Headers輸入
        ttk.Label(control_frame, text="Headers:").grid(row=1, column=0, sticky=(tk.W, tk.N), pady=(10, 0))
        self.headers_text = tk.Text(control_frame, height=3, width=60)
        self.headers_text.grid(row=1, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        self.headers_text.insert("1.0", "Content-Type: application/json\nAuthorization: Bearer your-token")

        # 下方內容面板
        content_frame = ttk.Frame(api_frame)
        content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)

        # 左側：請求體
        request_frame = ttk.LabelFrame(content_frame, text="請求體 (JSON)", padding="10")
        request_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        request_frame.columnconfigure(0, weight=1)
        request_frame.rowconfigure(0, weight=1)

        self.request_text = tk.Text(request_frame, wrap=tk.WORD, width=40, height=20,
                                   font=("Consolas", 10))
        request_scroll = ttk.Scrollbar(request_frame, orient="vertical", command=self.request_text.yview)
        self.request_text.configure(yscrollcommand=request_scroll.set)
        self.request_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        request_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # JSON檢查按鈕
        json_check_frame = ttk.Frame(request_frame)
        json_check_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        ttk.Button(json_check_frame, text="檢查JSON格式", command=self.check_json_format,
                  width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(json_check_frame, text="格式化JSON", command=self.format_json,
                  width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(json_check_frame, text="清除", command=self.clear_request,
                  width=10).pack(side=tk.LEFT)

        # 右側：響應
        response_frame = ttk.LabelFrame(content_frame, text="響應結果", padding="10")
        response_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        response_frame.columnconfigure(0, weight=1)
        response_frame.rowconfigure(0, weight=1)

        self.response_text = scrolledtext.ScrolledText(response_frame, wrap=tk.WORD,
                                                      width=40, height=20, font=("Consolas", 10))
        self.response_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 初始化JSON語法高亮
        self.json_highlighter = JSONSyntaxHighlighter(self.request_text)

        self.pages["api"] = api_frame

    def update_status(self, message):
        """更新狀態列"""
        self.status_var.set(message)
        self.root.update_idletasks()

    def append_result(self, text):
        """添加結果到顯示區域"""
        self.result_text.insert(tk.END, text + "\n")
        self.result_text.see(tk.END)
        self.root.update_idletasks()

    def clear_results(self):
        """清除結果顯示"""
        self.result_text.delete(1.0, tk.END)
        self.update_status("結果已清除")
    def scan_dhcp_servers(self):
        """掃描DHCP伺服器"""
        def scan_thread():
            try:
                self.update_status("正在掃描DHCP伺服器...")
                self.append_result("=== DHCP伺服器掃描 ===")

                # 執行掃描
                servers = self.dhcp_scanner.scan_dhcp_servers()

                if servers:
                    for server in servers:
                        self.append_result(f"DHCP伺服器: {server['ip']}")
                        self.append_result(f"MAC地址: {server['mac']}")
                        self.append_result(f"廠商: {server.get('vendor', '未知')}")
                        self.append_result("-" * 40)
                else:
                    self.append_result("未發現DHCP伺服器")

                self.update_status("DHCP掃描完成")

            except Exception as e:
                self.append_result(f"掃描錯誤: {str(e)}")
                self.update_status("DHCP掃描失敗")

        threading.Thread(target=scan_thread, daemon=True).start()
    def show_network_info(self):
        """顯示網路介面卡資訊"""
        def info_thread():
            try:
                self.update_status("正在獲取網路資訊...")
                self.append_result("=== 網路介面卡資訊 ===")

                # 獲取網路資訊
                interfaces = self.network_info.get_network_interfaces()

                for interface in interfaces:
                    self.append_result(f"介面名稱: {interface['name']}")
                    self.append_result(f"狀態: {interface['status']}")
                    self.append_result(f"IP地址: {interface.get('ip', 'N/A')}")
                    self.append_result(f"子網路遮罩: {interface.get('netmask', 'N/A')}")
                    self.append_result(f"MAC地址: {interface.get('mac', 'N/A')}")

                    # 顯示更多詳細資訊
                    if interface.get('speed', 'Unknown') != 'Unknown':
                        self.append_result(f"速度: {interface['speed']} Mbps")
                    if interface.get('mtu'):
                        self.append_result(f"MTU: {interface['mtu']}")
                    if interface.get('gateway'):
                        self.append_result(f"預設閘道: {interface['gateway']}")

                    # 顯示統計資訊
                    if 'statistics' in interface:
                        stats = interface['statistics']
                        sent_info = f"已傳送: {stats['bytes_sent']} ({stats['packets_sent']} 封包)"
                        recv_info = f"已接收: {stats['bytes_recv']} ({stats['packets_recv']} 封包)"
                        self.append_result(sent_info)
                        self.append_result(recv_info)
                        if stats['errors_in'] > 0 or stats['errors_out'] > 0:
                            error_info = f"錯誤: 輸入 {stats['errors_in']}, 輸出 {stats['errors_out']}"
                            self.append_result(error_info)

                    self.append_result("-" * 50)

                self.update_status("網路資訊獲取完成")

            except Exception as e:
                self.append_result(f"獲取網路資訊錯誤: {str(e)}")
                self.update_status("網路資訊獲取失敗")

        threading.Thread(target=info_thread, daemon=True).start()

    def test_internet(self):
        """測試外網連線"""
        def test_thread():
            try:
                self.update_status("正在測試外網連線...")
                self.append_result("=== 外網連線測試 ===")

                # 測試連線
                result = self.internet_test.test_connectivity()

                connected_status = "正常" if result['connected'] else "異常"
                self.append_result(f"外網連線狀態: {connected_status}")
                if result['connected']:
                    self.append_result(f"延遲: {result.get('ping', 'N/A')} ms")
                    dns_status = "正常" if result.get('dns', False) else "異常"
                    self.append_result(f"DNS解析: {dns_status}")
                else:
                    self.append_result(f"錯誤: {result.get('error', '未知錯誤')}")

                self.update_status("外網連線測試完成")

            except Exception as e:
                self.append_result(f"連線測試錯誤: {str(e)}")
                self.update_status("外網連線測試失敗")

        threading.Thread(target=test_thread, daemon=True).start()

    def test_speed(self):
        """測試網路速度"""
        def speed_thread():
            try:
                self.update_status("正在測試網路速度...")
                self.append_result("=== 網路速度測試 ===")
                self.append_result("正在測試，請稍候...")

                # 測試速度
                result = self.internet_test.test_speed()

                if result['success']:
                    self.append_result(f"下載速度: {result['download']:.2f} Mbps")
                    self.append_result(f"上傳速度: {result['upload']:.2f} Mbps")
                    self.append_result(f"延遲: {result['ping']:.2f} ms")
                    self.append_result(f"測試伺服器: {result.get('server', 'N/A')}")
                else:
                    error_msg = result.get('error', '未知錯誤')
                    self.append_result(f"速度測試失敗: {error_msg}")

                self.update_status("網路速度測試完成")

            except Exception as e:
                self.append_result(f"速度測試錯誤: {str(e)}")
                self.update_status("網路速度測試失敗")

        threading.Thread(target=speed_thread, daemon=True).start()
    def show_about(self):
        """顯示關於資訊"""
        about_text = """DHCP Finder v1.0

網路診斷工具

功能：
• DHCP伺服器掃描
• 網路介面卡資訊
• 外網連線測試
• 網路速度測試

開發者：Assistant
版本：1.0
"""
        messagebox.showinfo("關於", about_text)

    def send_api_request(self):
        """發送API請求"""
        def request_thread():
            try:
                self.update_status("正在發送API請求...")
                self.response_text.delete(1.0, tk.END)

                # 獲取請求參數
                method = self.method_var.get()
                url = self.url_var.get().strip()
                headers_text = self.headers_text.get("1.0", tk.END).strip()
                request_body = self.request_text.get("1.0", tk.END).strip()

                if not url:
                    self.response_text.insert(tk.END, "錯誤: 請輸入URL")
                    self.update_status("請求失敗")
                    return

                # 解析headers
                headers = self.api_tester.prepare_headers(headers_text)

                # 發送請求
                result = None
                if method == "GET":
                    result = self.api_tester.get_request(url, headers)
                elif method == "POST":
                    result = self.api_tester.post_request(url, headers, request_body)
                elif method == "PUT":
                    result = self.api_tester.put_request(url, headers, request_body)
                elif method == "DELETE":
                    result = self.api_tester.delete_request(url, headers)

                # 顯示結果
                if result:
                    self.display_api_response(result)
                self.update_status("API請求完成")

            except Exception as e:
                self.response_text.insert(tk.END, f"請求錯誤: {str(e)}")
                self.update_status("API請求失敗")

        threading.Thread(target=request_thread, daemon=True).start()

    def display_api_response(self, result):
        """顯示API響應結果"""
        self.response_text.delete(1.0, tk.END)

        if result['success']:
            # 顯示狀態和基本資訊
            status_text = result.get('status_text', '')
            self.response_text.insert(tk.END, f"狀態: {result['status_code']} {status_text}\n")
            self.response_text.insert(tk.END, f"響應時間: {result['response_time']} ms\n")
            self.response_text.insert(tk.END, f"內容大小: {result.get('size', 0)} bytes\n")
            self.response_text.insert(tk.END, f"編碼: {result.get('encoding', 'N/A')}\n\n")

            # 顯示響應頭
            self.response_text.insert(tk.END, "=== 響應頭 ===\n")
            for key, value in result.get('headers', {}).items():
                self.response_text.insert(tk.END, f"{key}: {value}\n")

            # 顯示響應體
            self.response_text.insert(tk.END, "\n=== 響應體 ===\n")
            formatted_content = result.get('formatted_content', result.get('content', ''))
            self.response_text.insert(tk.END, formatted_content)
        else:
            self.response_text.insert(tk.END, f"請求失敗: {result.get('error', '未知錯誤')}\n")
            if result.get('status_code'):
                self.response_text.insert(tk.END, f"狀態碼: {result['status_code']}\n")
            self.response_text.insert(tk.END, f"響應時間: {result.get('response_time', 0)} ms\n")

    def check_json_format(self):
        """檢查JSON格式"""
        json_content = self.request_text.get("1.0", tk.END).strip()
        if not json_content:
            messagebox.showinfo("JSON檢查", "請輸入JSON內容")
            return

        is_valid, message, _ = self.json_formatter.validate_json(json_content)

        if is_valid:
            messagebox.showinfo("JSON檢查", "✓ JSON格式正確")
            # 應用語法高亮
            self.json_highlighter.highlight_json()
        else:
            messagebox.showerror("JSON檢查", f"✗ JSON格式錯誤\n\n{message}")
            # 高亮錯誤
            self.json_highlighter.highlight_errors(json_content)

    def format_json(self):
        """格式化JSON"""
        json_content = self.request_text.get("1.0", tk.END).strip()
        if not json_content:
            messagebox.showinfo("格式化", "請輸入JSON內容")
            return

        try:
            formatted = self.json_formatter.format_json(json_content)
            self.request_text.delete("1.0", tk.END)
            self.request_text.insert("1.0", formatted)
            # 應用語法高亮
            self.json_highlighter.highlight_json()
            messagebox.showinfo("格式化", "JSON格式化完成")
        except Exception as e:
            messagebox.showerror("格式化", f"格式化失敗: {str(e)}")

    def clear_request(self):
        """清除請求內容"""
        self.request_text.delete("1.0", tk.END)

    def clear_response(self):
        """清除響應內容"""
        self.response_text.delete(1.0, tk.END)


def main():
    """主函數"""
    # 檢查是否以管理員身份執行
    try:
        import ctypes  # pylint: disable=import-outside-toplevel
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        if not is_admin:
            warning_msg = "建議以管理員身份執行此程式以獲得完整功能"
            messagebox.showwarning("權限警告", warning_msg)
    except (ImportError, AttributeError, OSError):
        pass

    # 創建主視窗
    root = tk.Tk()
    DHCPFinderGUI(root)  # 不需要保存引用，GUI會自己管理

    # 設置視窗圖示（如果有的話）
    try:
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller環境
            # pylint: disable=protected-access
            icon_path = os.path.join(sys._MEIPASS, 'icon.ico')
        else:
            icon_path = 'icon.ico'
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
    except (AttributeError, OSError, tk.TclError):
        pass

    # 啟動GUI
    root.mainloop()


if __name__ == "__main__":
    main()
