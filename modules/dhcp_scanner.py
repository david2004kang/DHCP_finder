# -*- coding: utf-8 -*-
"""
DHCP伺服器掃描模組
功能：掃描網路中的DHCP伺服器並獲取其MAC地址
"""

import socket
import struct
import time
import threading
import netifaces
from scapy.all import *
import psutil


class DHCPScanner:
    """DHCP伺服器掃描器"""
    
    def __init__(self):
        self.dhcp_servers = []
        self.scan_timeout = 10  # 掃描超時時間（秒）
        
    def get_mac_vendor(self, mac_address):
        """獲取MAC地址廠商資訊"""
        # 簡化的廠商識別，實際應用可以使用更完整的OUI資料庫
        oui_dict = {
            '00:50:56': 'VMware',
            '08:00:27': 'VirtualBox',
            '00:0C:29': 'VMware',
            '00:1C:42': 'Parallels',
            '00:15:5D': 'Microsoft Hyper-V',
            '52:54:00': 'QEMU/KVM',
            'B8:27:EB': 'Raspberry Pi',
            '00:16:3E': 'Xen',
        }
        
        mac_prefix = mac_address[:8].upper()
        return oui_dict.get(mac_prefix, '未知廠商')
        
    def create_dhcp_discover_packet(self, client_mac):
        """創建DHCP Discover封包"""
        # DHCP Discover封包結構
        packet = b''
        packet += b'\x01'  # Message type: Boot Request (1)
        packet += b'\x01'  # Hardware type: Ethernet (1)
        packet += b'\x06'  # Hardware address length: 6
        packet += b'\x00'  # Hops: 0
        
        # Transaction ID (隨機)
        xid = struct.pack('!I', int(time.time()) & 0xFFFFFFFF)
        packet += xid
        
        packet += b'\x00\x00'  # Seconds elapsed: 0
        packet += b'\x00\x00'  # Bootp flags: 0
        packet += b'\x00\x00\x00\x00'  # Client IP address: 0.0.0.0
        packet += b'\x00\x00\x00\x00'  # Your (client) IP address: 0.0.0.0
        packet += b'\x00\x00\x00\x00'  # Next server IP address: 0.0.0.0
        packet += b'\x00\x00\x00\x00'  # Relay agent IP address: 0.0.0.0
        
        # Client MAC address
        mac_bytes = bytes.fromhex(client_mac.replace(':', ''))
        packet += mac_bytes + b'\x00' * (16 - len(mac_bytes))
        
        # Server host name (64 bytes)
        packet += b'\x00' * 64
        
        # Boot file name (128 bytes)
        packet += b'\x00' * 128
        
        # Magic cookie
        packet += b'\x63\x82\x53\x63'
        
        # DHCP options
        packet += b'\x35\x01\x01'  # DHCP Message Type: Discover
        packet += b'\x37\x04\x01\x03\x06\x2a'  # Parameter Request List
        packet += b'\xff'  # End Option
        
        return packet
        
    def scan_dhcp_with_socket(self):
        """使用Socket方式掃描DHCP伺服器"""
        dhcp_servers = []
        
        try:
            # 獲取本機網路介面
            interfaces = netifaces.interfaces()
            
            for interface in interfaces:
                try:
                    # 獲取介面資訊
                    addrs = netifaces.ifaddresses(interface)
                    if netifaces.AF_INET not in addrs:
                        continue
                        
                    # 獲取IP和廣播地址
                    inet_info = addrs[netifaces.AF_INET][0]
                    if 'broadcast' not in inet_info:
                        continue
                        
                    broadcast_addr = inet_info['broadcast']
                    local_ip = inet_info['addr']
                    
                    # 獲取MAC地址
                    if netifaces.AF_LINK in addrs:
                        mac_addr = addrs[netifaces.AF_LINK][0]['addr']
                    else:
                        mac_addr = '00:00:00:00:00:00'
                    
                    # 創建UDP socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    sock.settimeout(3)
                    
                    try:
                        # 綁定到DHCP客戶端端口
                        sock.bind((local_ip, 68))
                        
                        # 創建DHCP Discover封包
                        dhcp_packet = self.create_dhcp_discover_packet(mac_addr)
                        
                        # 發送到廣播地址
                        sock.sendto(dhcp_packet, (broadcast_addr, 67))
                        
                        # 接收回應
                        start_time = time.time()
                        while time.time() - start_time < 3:
                            try:
                                data, addr = sock.recvfrom(1024)
                                if len(data) > 240:  # DHCP封包最小長度
                                    server_info = {
                                        'ip': addr[0],
                                        'mac': 'Unknown',
                                        'vendor': 'Unknown',
                                        'interface': interface
                                    }
                                    
                                    # 避免重複
                                    if not any(s['ip'] == addr[0] for s in dhcp_servers):
                                        dhcp_servers.append(server_info)
                                        
                            except socket.timeout:
                                break
                                
                    except Exception as e:
                        print(f"Interface {interface} error: {e}")
                    finally:
                        sock.close()
                        
                except Exception as e:
                    print(f"Processing interface {interface} failed: {e}")
                    continue
                    
        except Exception as e:
            print(f"DHCP scan error: {e}")
            
        return dhcp_servers
        
    def scan_dhcp_with_scapy(self):
        """使用Scapy方式掃描DHCP伺服器"""
        dhcp_servers = []
        
        try:
            # 獲取所有網路介面
            interfaces = [iface for iface in netifaces.interfaces() 
                         if not iface.startswith('Loopback')]
            
            for interface in interfaces:
                try:
                    # 獲取介面資訊
                    addrs = netifaces.ifaddresses(interface)
                    if netifaces.AF_INET not in addrs:
                        continue
                        
                    inet_info = addrs[netifaces.AF_INET][0]
                    if 'broadcast' not in inet_info:
                        continue
                        
                    # 創建DHCP Discover封包
                    dhcp_discover = (
                        Ether(dst="ff:ff:ff:ff:ff:ff") /
                        IP(src="0.0.0.0", dst="255.255.255.255") /
                        UDP(sport=68, dport=67) /
                        BOOTP(chaddr=RandString(12, "0123456789abcdef")) /
                        DHCP(options=[("message-type", "discover"), "end"])
                    )
                    
                    # 發送封包並接收回應
                    responses = srp(dhcp_discover, timeout=3, verbose=0, 
                                  iface=interface)[0]
                    
                    for sent, received in responses:
                        if received.haslayer(DHCP):
                            server_ip = received[IP].src
                            server_mac = received[Ether].src
                            
                            server_info = {
                                'ip': server_ip,
                                'mac': server_mac,
                                'vendor': self.get_mac_vendor(server_mac),
                                'interface': interface
                            }
                            
                            # 避免重複
                            if not any(s['ip'] == server_ip for s in dhcp_servers):
                                dhcp_servers.append(server_info)
                                
                except Exception as e:
                    print(f"Scapy scan on {interface} failed: {e}")
                    continue
                    
        except Exception as e:
            print(f"Scapy DHCP scan error: {e}")
            
        return dhcp_servers
        
    def get_arp_table(self):
        """獲取ARP表以補充MAC地址資訊"""
        arp_table = {}
        
        try:
            # 在Windows上使用arp命令
            import subprocess
            result = subprocess.run(['arp', '-a'], capture_output=True, 
                                  text=True, timeout=10)
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'dynamic' in line.lower() or 'static' in line.lower():
                        parts = line.split()
                        if len(parts) >= 2:
                            ip = parts[0].strip()
                            mac = parts[1].strip()
                            if mac != '---':
                                arp_table[ip] = mac
                                
        except Exception as e:
            print(f"ARP table error: {e}")
            
        return arp_table
        
    def scan_dhcp_servers(self):
        """掃描DHCP伺服器主函數"""
        print("開始掃描DHCP伺服器...")
        
        # 嘗試多種掃描方法
        dhcp_servers = []
        
        # 方法1：使用Socket
        try:
            socket_results = self.scan_dhcp_with_socket()
            dhcp_servers.extend(socket_results)
        except Exception as e:
            print(f"Socket掃描失敗: {e}")
            
        # 方法2：使用Scapy（需要管理員權限）
        try:
            scapy_results = self.scan_dhcp_with_scapy()
            dhcp_servers.extend(scapy_results)
        except Exception as e:
            print(f"Scapy掃描失敗: {e}")
            
        # 獲取ARP表補充MAC地址
        arp_table = self.get_arp_table()
        
        # 補充MAC地址資訊
        for server in dhcp_servers:
            if server['mac'] == 'Unknown' and server['ip'] in arp_table:
                server['mac'] = arp_table[server['ip']]
                server['vendor'] = self.get_mac_vendor(server['mac'])
                
        # 去除重複
        unique_servers = []
        seen_ips = set()
        
        for server in dhcp_servers:
            if server['ip'] not in seen_ips:
                unique_servers.append(server)
                seen_ips.add(server['ip'])
                
        print(f"掃描完成，發現 {len(unique_servers)} 個DHCP伺服器")
        return unique_servers


if __name__ == "__main__":
    # 測試代碼
    scanner = DHCPScanner()
    servers = scanner.scan_dhcp_servers()
    
    if servers:
        print("\n發現的DHCP伺服器：")
        for server in servers:
            print(f"IP: {server['ip']}")
            print(f"MAC: {server['mac']}")
            print(f"廠商: {server['vendor']}")
            print(f"介面: {server['interface']}")
            print("-" * 30)
    else:
        print("未發現DHCP伺服器")
