# -*- coding: utf-8 -*-
"""
外網連線及網速測試模組
功能：檢測外網連線狀態並測試網路速度
"""

import socket
import time
import subprocess
import platform
import requests
import speedtest
import threading
from urllib.parse import urlparse


class InternetTest:
    """外網連線及網速測試器"""
    
    def __init__(self):
        self.system = platform.system()
        self.test_hosts = [
            ('8.8.8.8', 53),      # Google DNS
            ('1.1.1.1', 53),      # Cloudflare DNS
            ('208.67.222.222', 53), # OpenDNS
            ('google.com', 80),    # Google HTTP
            ('microsoft.com', 80)  # Microsoft HTTP
        ]
        self.test_urls = [
            'http://www.google.com',
            'http://www.microsoft.com',
            'http://www.cloudflare.com'
        ]
        
    def ping_host(self, host, timeout=3):
        """Ping指定主機"""
        try:
            if self.system == "Windows":
                cmd = ['ping', '-n', '1', '-w', str(timeout * 1000), host]
            else:
                cmd = ['ping', '-c', '1', '-W', str(timeout), host]
                
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 2)
            
            if result.returncode == 0:
                # 解析ping結果獲取延遲時間
                output = result.stdout
                if self.system == "Windows":
                    # Windows: time=1ms 或 time<1ms
                    import re
                    time_match = re.search(r'time[<=](\d+)ms', output)
                    if time_match:
                        return float(time_match.group(1))
                    time_match = re.search(r'time=(\d+)ms', output)
                    if time_match:
                        return float(time_match.group(1))
                else:
                    # Linux: time=1.23 ms
                    import re
                    time_match = re.search(r'time=([0-9.]+)\s*ms', output)
                    if time_match:
                        return float(time_match.group(1))
                        
                return 0  # 成功但無法解析時間
            else:
                return None
                
        except Exception as e:
            print(f"Ping {host} 錯誤: {e}")
            return None
            
    def test_socket_connection(self, host, port, timeout=3):
        """測試Socket連線"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            start_time = time.time()
            result = sock.connect_ex((host, port))
            end_time = time.time()
            
            sock.close()
            
            if result == 0:
                return (end_time - start_time) * 1000  # 轉換為毫秒
            else:
                return None
                
        except Exception as e:
            print(f"Socket連線 {host}:{port} 錯誤: {e}")
            return None
            
    def test_http_connection(self, url, timeout=5):
        """測試HTTP連線"""
        try:
            start_time = time.time()
            response = requests.get(url, timeout=timeout, allow_redirects=True)
            end_time = time.time()
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'response_time': (end_time - start_time) * 1000,
                    'status_code': response.status_code,
                    'content_length': len(response.content)
                }
            else:
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'error': f'HTTP {response.status_code}'
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e)
            }
            
    def test_dns_resolution(self, hostname):
        """測試DNS解析"""
        try:
            start_time = time.time()
            socket.gethostbyname(hostname)
            end_time = time.time()
            
            return {
                'success': True,
                'response_time': (end_time - start_time) * 1000
            }
            
        except socket.gaierror as e:
            return {
                'success': False,
                'error': str(e)
            }
            
    def test_connectivity(self):
        """綜合連線測試"""
        results = {
            'connected': False,
            'ping': None,
            'dns': False,
            'http': False,
            'details': []
        }
        
        successful_tests = 0
        total_tests = 0
        ping_times = []
        
        # 測試Ping連線
        print("測試Ping連線...")
        for host, port in self.test_hosts:
            if isinstance(host, str) and '.' in host and host.replace('.', '').isdigit():
                # IP地址，使用ping
                ping_time = self.ping_host(host)
                total_tests += 1
                
                if ping_time is not None:
                    successful_tests += 1
                    ping_times.append(ping_time)
                    results['details'].append({
                        'test': f'Ping {host}',
                        'success': True,
                        'time': ping_time
                    })
                else:
                    results['details'].append({
                        'test': f'Ping {host}',
                        'success': False,
                        'error': 'Timeout or unreachable'
                    })
            else:
                # 主機名，測試Socket連線
                conn_time = self.test_socket_connection(host, port)
                total_tests += 1
                
                if conn_time is not None:
                    successful_tests += 1
                    ping_times.append(conn_time)
                    results['details'].append({
                        'test': f'Socket {host}:{port}',
                        'success': True,
                        'time': conn_time
                    })
                else:
                    results['details'].append({
                        'test': f'Socket {host}:{port}',
                        'success': False,
                        'error': 'Connection failed'
                    })
                    
        # 測試DNS解析
        print("測試DNS解析...")
        dns_result = self.test_dns_resolution('google.com')
        if dns_result['success']:
            results['dns'] = True
            results['details'].append({
                'test': 'DNS Resolution',
                'success': True,
                'time': dns_result['response_time']
            })
        else:
            results['details'].append({
                'test': 'DNS Resolution',
                'success': False,
                'error': dns_result['error']
            })
            
        # 測試HTTP連線
        print("測試HTTP連線...")
        for url in self.test_urls:
            http_result = self.test_http_connection(url)
            total_tests += 1
            
            if http_result['success']:
                successful_tests += 1
                results['http'] = True
                results['details'].append({
                    'test': f'HTTP {url}',
                    'success': True,
                    'time': http_result['response_time']
                })
            else:
                results['details'].append({
                    'test': f'HTTP {url}',
                    'success': False,
                    'error': http_result['error']
                })
                
        # 計算平均延遲
        if ping_times:
            results['ping'] = sum(ping_times) / len(ping_times)
            
        # 判斷整體連線狀態
        if successful_tests > 0:
            results['connected'] = True
            
        return results
        
    def test_speed(self):
        """網路速度測試"""
        try:
            print("初始化速度測試...")
            st = speedtest.Speedtest()
            
            print("獲取最佳伺服器...")
            st.get_best_server()
            
            print("測試下載速度...")
            download_speed = st.download()
            
            print("測試上傳速度...")
            upload_speed = st.upload()
            
            # 獲取伺服器資訊
            server_info = st.results.server
            
            return {
                'success': True,
                'download': download_speed / 1_000_000,  # 轉換為Mbps
                'upload': upload_speed / 1_000_000,      # 轉換為Mbps
                'ping': st.results.ping,
                'server': f"{server_info['sponsor']} - {server_info['name']}, {server_info['country']}",
                'server_id': server_info['id'],
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
            
    def test_speed_alternative(self):
        """替代的速度測試方法（使用HTTP下載）"""
        test_files = [
            {
                'url': 'http://speedtest.ftp.otenet.gr/files/test1Mb.db',
                'size': 1 * 1024 * 1024,  # 1MB
                'name': '1MB Test File'
            },
            {
                'url': 'http://speedtest.ftp.otenet.gr/files/test10Mb.db',
                'size': 10 * 1024 * 1024,  # 10MB
                'name': '10MB Test File'
            }
        ]
        
        results = []
        
        for test_file in test_files:
            try:
                print(f"下載測試檔案: {test_file['name']}")
                
                start_time = time.time()
                response = requests.get(test_file['url'], timeout=30, stream=True)
                
                if response.status_code == 200:
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        downloaded += len(chunk)
                        
                    end_time = time.time()
                    duration = end_time - start_time
                    
                    if duration > 0:
                        speed_bps = downloaded / duration
                        speed_mbps = speed_bps / 1_000_000
                        
                        results.append({
                            'file': test_file['name'],
                            'size': downloaded,
                            'duration': duration,
                            'speed_mbps': speed_mbps
                        })
                        
            except Exception as e:
                print(f"下載測試失敗 {test_file['name']}: {e}")
                continue
                
        if results:
            avg_speed = sum(r['speed_mbps'] for r in results) / len(results)
            return {
                'success': True,
                'download': avg_speed,
                'upload': 0,  # 此方法無法測試上傳
                'ping': 0,
                'details': results,
                'method': 'HTTP Download Test'
            }
        else:
            return {
                'success': False,
                'error': 'All download tests failed'
            }
            
    def get_public_ip(self):
        """獲取公網IP地址"""
        services = [
            'https://api.ipify.org',
            'https://ipinfo.io/ip',
            'https://icanhazip.com',
            'https://ident.me'
        ]
        
        for service in services:
            try:
                response = requests.get(service, timeout=5)
                if response.status_code == 200:
                    ip = response.text.strip()
                    # 簡單驗證IP格式
                    parts = ip.split('.')
                    if len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts):
                        return ip
            except:
                continue
                
        return None


if __name__ == "__main__":
    # 測試代碼
    internet_test = InternetTest()
    
    print("測試外網連線...")
    connectivity = internet_test.test_connectivity()
    print(f"連線狀態: {'正常' if connectivity['connected'] else '異常'}")
    if connectivity['ping']:
        print(f"平均延遲: {connectivity['ping']:.2f} ms")
        
    print("\n測試網路速度...")
    speed_result = internet_test.test_speed()
    if speed_result['success']:
        print(f"下載速度: {speed_result['download']:.2f} Mbps")
        print(f"上傳速度: {speed_result['upload']:.2f} Mbps")
    else:
        print(f"速度測試失敗: {speed_result['error']}")
        
    print("\n獲取公網IP...")
    public_ip = internet_test.get_public_ip()
    if public_ip:
        print(f"公網IP: {public_ip}")
    else:
        print("無法獲取公網IP")
