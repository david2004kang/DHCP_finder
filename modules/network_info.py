# -*- coding: utf-8 -*-
"""
網路介面卡資訊模組
功能：獲取本機網路介面卡的詳細資訊
"""

import psutil
import netifaces
import socket
import subprocess
import platform
import re


class NetworkInfo:
    """網路資訊獲取器"""
    
    def __init__(self):
        self.system = platform.system()
        
    def get_interface_status(self, interface_name):
        """獲取網路介面狀態"""
        try:
            stats = psutil.net_if_stats()
            if interface_name in stats:
                stat = stats[interface_name]
                return {
                    'is_up': stat.isup,
                    'speed': stat.speed if stat.speed > 0 else 'Unknown',
                    'mtu': stat.mtu,
                    'duplex': self._get_duplex_name(stat.duplex)
                }
        except Exception as e:
            print(f"獲取介面狀態錯誤: {e}")
            
        return {
            'is_up': False,
            'speed': 'Unknown',
            'mtu': 'Unknown',
            'duplex': 'Unknown'
        }
        
    def _get_duplex_name(self, duplex_value):
        """轉換duplex值為可讀名稱"""
        duplex_map = {
            0: 'Unknown',
            1: 'Half',
            2: 'Full'
        }
        return duplex_map.get(duplex_value, 'Unknown')
        
    def get_gateway_info(self):
        """獲取預設閘道資訊"""
        gateways = {}
        try:
            gw_info = netifaces.gateways()
            if 'default' in gw_info:
                default_gw = gw_info['default']
                if netifaces.AF_INET in default_gw:
                    gw_ip, interface = default_gw[netifaces.AF_INET]
                    gateways['default'] = {
                        'ip': gw_ip,
                        'interface': interface
                    }
                    
            # 獲取所有閘道
            for family, gw_list in gw_info.items():
                if family != 'default' and isinstance(gw_list, list):
                    for gw_ip, interface, is_default in gw_list:
                        if interface not in gateways:
                            gateways[interface] = []
                        gateways[interface].append({
                            'ip': gw_ip,
                            'is_default': is_default
                        })
                        
        except Exception as e:
            print(f"獲取閘道資訊錯誤: {e}")
            
        return gateways
        
    def get_dns_servers(self):
        """獲取DNS伺服器資訊"""
        dns_servers = []
        
        try:
            if self.system == "Windows":
                # Windows系統使用nslookup獲取DNS
                result = subprocess.run(['nslookup', 'google.com'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if 'Server:' in line:
                            dns_ip = line.split(':')[-1].strip()
                            if dns_ip and dns_ip != '127.0.0.1':
                                dns_servers.append(dns_ip)
                                
                # 也嘗試從ipconfig獲取
                result = subprocess.run(['ipconfig', '/all'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    dns_pattern = r'DNS Servers.*?:\s*([0-9.]+)'
                    matches = re.findall(dns_pattern, result.stdout)
                    for match in matches:
                        if match not in dns_servers:
                            dns_servers.append(match)
                            
            else:
                # Linux/Unix系統讀取/etc/resolv.conf
                try:
                    with open('/etc/resolv.conf', 'r') as f:
                        for line in f:
                            if line.startswith('nameserver'):
                                dns_ip = line.split()[1]
                                dns_servers.append(dns_ip)
                except:
                    pass
                    
        except Exception as e:
            print(f"獲取DNS伺服器錯誤: {e}")
            
        return list(set(dns_servers))  # 去除重複
        
    def get_network_statistics(self, interface_name):
        """獲取網路介面統計資訊"""
        try:
            stats = psutil.net_io_counters(pernic=True)
            if interface_name in stats:
                stat = stats[interface_name]
                return {
                    'bytes_sent': stat.bytes_sent,
                    'bytes_recv': stat.bytes_recv,
                    'packets_sent': stat.packets_sent,
                    'packets_recv': stat.packets_recv,
                    'errin': stat.errin,
                    'errout': stat.errout,
                    'dropin': stat.dropin,
                    'dropout': stat.dropout
                }
        except Exception as e:
            print(f"獲取網路統計錯誤: {e}")
            
        return None
        
    def format_bytes(self, bytes_value):
        """格式化位元組數值"""
        if bytes_value == 0:
            return "0 B"
            
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        
        while bytes_value >= 1024 and unit_index < len(units) - 1:
            bytes_value /= 1024
            unit_index += 1
            
        return f"{bytes_value:.2f} {units[unit_index]}"
        
    def get_network_interfaces(self):
        """獲取所有網路介面資訊"""
        interfaces = []
        
        try:
            # 獲取閘道資訊
            gateways = self.get_gateway_info()
            
            # 獲取DNS伺服器
            dns_servers = self.get_dns_servers()
            
            # 遍歷所有網路介面
            for interface_name in netifaces.interfaces():
                try:
                    # 跳過Loopback介面
                    if 'Loopback' in interface_name or interface_name.startswith('lo'):
                        continue
                        
                    interface_info = {
                        'name': interface_name,
                        'display_name': interface_name,
                        'status': 'Unknown',
                        'type': 'Unknown',
                        'addresses': []
                    }
                    
                    # 獲取介面狀態
                    status_info = self.get_interface_status(interface_name)
                    interface_info['status'] = 'Up' if status_info['is_up'] else 'Down'
                    interface_info['speed'] = status_info['speed']
                    interface_info['mtu'] = status_info['mtu']
                    interface_info['duplex'] = status_info['duplex']
                    
                    # 獲取地址資訊
                    addrs = netifaces.ifaddresses(interface_name)
                    
                    # IPv4地址
                    if netifaces.AF_INET in addrs:
                        for addr_info in addrs[netifaces.AF_INET]:
                            interface_info['ip'] = addr_info.get('addr', 'N/A')
                            interface_info['netmask'] = addr_info.get('netmask', 'N/A')
                            interface_info['broadcast'] = addr_info.get('broadcast', 'N/A')
                            
                            interface_info['addresses'].append({
                                'family': 'IPv4',
                                'address': addr_info.get('addr', 'N/A'),
                                'netmask': addr_info.get('netmask', 'N/A'),
                                'broadcast': addr_info.get('broadcast', 'N/A')
                            })
                            
                    # IPv6地址
                    if netifaces.AF_INET6 in addrs:
                        for addr_info in addrs[netifaces.AF_INET6]:
                            interface_info['addresses'].append({
                                'family': 'IPv6',
                                'address': addr_info.get('addr', 'N/A'),
                                'netmask': addr_info.get('netmask', 'N/A')
                            })
                            
                    # MAC地址
                    if netifaces.AF_LINK in addrs:
                        mac_info = addrs[netifaces.AF_LINK][0]
                        interface_info['mac'] = mac_info.get('addr', 'N/A')
                        
                    # 閘道資訊
                    if interface_name in gateways:
                        interface_info['gateways'] = gateways[interface_name]
                    elif 'default' in gateways and gateways['default']['interface'] == interface_name:
                        interface_info['gateway'] = gateways['default']['ip']
                        interface_info['is_default'] = True
                        
                    # 網路統計
                    stats = self.get_network_statistics(interface_name)
                    if stats:
                        interface_info['statistics'] = {
                            'bytes_sent': self.format_bytes(stats['bytes_sent']),
                            'bytes_recv': self.format_bytes(stats['bytes_recv']),
                            'packets_sent': stats['packets_sent'],
                            'packets_recv': stats['packets_recv'],
                            'errors_in': stats['errin'],
                            'errors_out': stats['errout'],
                            'drops_in': stats['dropin'],
                            'drops_out': stats['dropout']
                        }
                        
                    # DNS伺服器（只在主要介面顯示）
                    if interface_info.get('is_default', False):
                        interface_info['dns_servers'] = dns_servers
                        
                    interfaces.append(interface_info)
                    
                except Exception as e:
                    print(f"處理介面 {interface_name} 時發生錯誤: {e}")
                    continue
                    
        except Exception as e:
            print(f"獲取網路介面錯誤: {e}")
            
        return interfaces
        
    def get_routing_table(self):
        """獲取路由表資訊"""
        routes = []
        
        try:
            if self.system == "Windows":
                result = subprocess.run(['route', 'print'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    in_ipv4_section = False
                    
                    for line in lines:
                        line = line.strip()
                        if 'IPv4 Route Table' in line:
                            in_ipv4_section = True
                            continue
                        elif 'IPv6 Route Table' in line:
                            in_ipv4_section = False
                            continue
                            
                        if in_ipv4_section and line:
                            parts = line.split()
                            if len(parts) >= 5 and parts[0].replace('.', '').isdigit():
                                routes.append({
                                    'destination': parts[0],
                                    'netmask': parts[1],
                                    'gateway': parts[2],
                                    'interface': parts[3],
                                    'metric': parts[4]
                                })
                                
        except Exception as e:
            print(f"獲取路由表錯誤: {e}")
            
        return routes


if __name__ == "__main__":
    # 測試代碼
    network_info = NetworkInfo()
    interfaces = network_info.get_network_interfaces()
    
    print("網路介面資訊：")
    for interface in interfaces:
        print(f"\n介面名稱: {interface['name']}")
        print(f"狀態: {interface['status']}")
        print(f"IP地址: {interface.get('ip', 'N/A')}")
        print(f"MAC地址: {interface.get('mac', 'N/A')}")
        print(f"速度: {interface.get('speed', 'N/A')}")
        print("-" * 40)
