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


class DHCPFinderGUI:
    """DHCP Finder 主要GUI類別"""

    def __init__(self, root):
        self.root = root
        self.root.title("DHCP Finder - 網路工具 v1.0")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # 初始化功能模組
        self.dhcp_scanner = DHCPScanner()
        self.network_info = NetworkInfo()
        self.internet_test = InternetTest()

        self.setup_ui()

    def setup_ui(self):
        """設置使用者介面"""
        # 創建主要框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置網格權重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # 標題
        title_label = ttk.Label(main_frame, text="DHCP Finder - 網路診斷工具",
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # 左側按鈕面板
        button_frame = ttk.LabelFrame(main_frame, text="功能選單", padding="10")
        button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

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
        result_frame = ttk.LabelFrame(main_frame, text="結果顯示", padding="10")
        result_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)

        # 結果文字區域
        self.result_text = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD,
                                                    width=50, height=25)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 狀態列
        self.status_var = tk.StringVar()
        self.status_var.set("就緒")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var,
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

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
