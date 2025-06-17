# happy uses 
#!/usr/bin/env python3
import subprocess
import re
import argparse
import time

class DomainAnalyzer:
    def __init__(self, timeout=5):
        self.timeout = timeout
    
    def run_command(self, command):
        try:
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                timeout=self.timeout
            )
            return result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return None, f"Timeout: {' '.join(command)}"
        except Exception as e:
            return None, f"Hata: {e}"
    
    def get_nameservers(self, domain):
        """Name server bilgilerini çıkar"""
        stdout, stderr = self.run_command(['host', '-t', 'ns', domain])
        if not stdout:
            return [f"HATA: {stderr}"]
        
        nameservers = []
        for line in stdout.splitlines():
            if 'name server' in line.lower():
                parts = line.split()
                if len(parts) >= 4:
                    ns = parts[-1].rstrip('.')
                    nameservers.append(ns)
        
        return nameservers if nameservers else ["Nameserver bulunamadi"]
    
    def get_mailservers(self, domain):
        """Mail server bilgilerini çek"""
        stdout, stderr = self.run_command(['host', '-t', 'mx', domain])
        if not stdout:
            return [f"HATA: {stderr}"]
        
        mailservers = []
        for line in stdout.splitlines():
            if 'mail is handled by' in line.lower():
                parts = line.split()
                if len(parts) >= 6:
                    priority = parts[4]
                    server = parts[5].rstrip('.')
                    mailservers.append(f"{priority} {server}")
        
        return mailservers if mailservers else ["Mail server bulunamadi"]
    
    def get_ipv4_addresses(self, domain):
        """IPv4 adreslerini al"""
        stdout, stderr = self.run_command(['host', '-t', 'a', domain])
        if not stdout:
            return [f"HATA: {stderr}"]
        
        # Regex ile IP adreslerini bul
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        ip_addresses = re.findall(ip_pattern, stdout)
        
        return ip_addresses if ip_addresses else ["IPv4 adresi bulunamadi"]
    
    def get_http_info(self, domain):
        """HTTP bilgilerini çek"""
        # Önce https dene
        for protocol in ['https', 'http']:
            url = f"{protocol}://{domain}"
            stdout, stderr = self.run_command(['curl', '-I', url])
            
            if stdout:
                return self.parse_http_response(stdout)
        
        return {
            'status': 'Sunucuya ulasilamiyor',
            'server': 'Bilinmiyor',
            'location': 'Yok'
        }
    
    def parse_http_response(self, response):
        """HTTP yanıtını parse et"""
        info = {
            'status': 'Bilinmiyor',
            'server': 'Bilinmiyor', 
            'location': 'Yok'
        }
        
        # HTTP status code
        status_match = re.search(r'HTTP/[\d.]+\s+(\d+)', response)
        if status_match:
            info['status'] = status_match.group(1)
        
        # Server bilgisi
        server_match = re.search(r'^Server:\s*(.+)$', response, re.MULTILINE)
        if server_match:
            info['server'] = server_match.group(1).strip()
        
        # Location (redirect)
        location_match = re.search(r'^Location:\s*(.+)$', response, re.MULTILINE)
        if location_match:
            info['location'] = location_match.group(1).strip()
        
        return info
    
    def analyze(self, domain):
        """Domain analizi yap"""
        print(f"\n{domain} analiz ediliyor...\n")
        
        # Nameservers
        print("Nameservers:")
        nameservers = self.get_nameservers(domain)
        for ns in nameservers:
            print(f"  {ns}")
        
        # Mail servers
        print("\nMail Servers:")
        mailservers = self.get_mailservers(domain)
        for ms in mailservers:
            print(f"  {ms}")
        
        # IPv4 addresses
        print("\nIPv4 Addresses:")
        ipv4_addrs = self.get_ipv4_addresses(domain)
        for ip in ipv4_addrs:
            print(f"  {ip}")
        
        # HTTP info
        print("\nHTTP Bilgileri:")
        http_info = self.get_http_info(domain)
        print(f"  Status: {http_info['status']}")
        print(f"  Server: {http_info['server']}")
        if http_info['location'] != 'Yok':
            print(f"  Redirect: {http_info['location']}")

def main():
    parser = argparse.ArgumentParser(description="Domain analiz araci")
    parser.add_argument("domain", help="Analiz edilecek domain")
    parser.add_argument("-t", "--timeout", type=int, default=5, 
                       help="Timeout suresi (saniye)")
    
    args = parser.parse_args()
    
    try:
        analyzer = DomainAnalyzer(timeout=args.timeout)
        analyzer.analyze(args.domain)
    except KeyboardInterrupt:
        print("\nIslem iptal edildi.")
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    main()
