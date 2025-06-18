# happy uses 
#!/usr/bin/env python3
import subprocess
import re
import argparse
import time

def get_name_servers(site_ad, timeout):
    try:
        result = subprocess.run(['host', '-t', 'ns', site_ad], capture_output=True, text=True, timeout=timeout)
        return result.stdout
    except subprocess.TimeoutExpired:
        return f"HATA [{site_ad} cevap vermedi.]\n"
    except Exception as e:
        return f"HATA {site_ad}: {e}\n"

def get_mail_servers(site_ad, timeout):
    try:
        result = subprocess.run(['host', '-t', 'mx', site_ad], capture_output=True, text=True, timeout=timeout)
        return result.stdout
    except subprocess.TimeoutExpired:
        return f"HATA [{site_ad} cevap vermedi.]\n"
    except Exception as e:
        return f"HATA {site_ad}: {e}\n"

def get_ipv4_addresses(site_ad, timeout):
    try:
        result = subprocess.run(['host', '-t', 'a', site_ad], capture_output=True, text=True, timeout=timeout)
        return result.stdout
    except subprocess.TimeoutExpired:
        return f"HATA [{site_ad} cevap vermedi.]\n"
    except Exception as e:
        return f"HATA {site_ad}: {e}\n"

def get_http_headers(site_ad, timeout):
    # HTTP ve HTTPS'i dene
    for protocol in ['https://', 'http://']:
        try:
            url = f"{protocol}{site_ad}"
            result = subprocess.run(['curl', '-I', url], capture_output=True, text=True, timeout=timeout)
            if result.returncode == 0:
                return result.stdout
        except subprocess.TimeoutExpired:
            continue
        except Exception:
            continue
    return f"HATA [{site_ad} HTTP/HTTPS cevap vermedi.]\n"

def main(site_ad):
    timeout = 5
    
    print(f"\n{site_ad}\n")
    
    # NameServer
    ns_output = get_name_servers(site_ad, timeout)
    for line in ns_output.splitlines():
        if "name server" in line:
            words = line.split()
            if len(words) >= 4:
                ns_sonuc = ' '.join(words[3:])
                print(f"Nameserver: [{ns_sonuc}]")
        elif "HATA" in line:
            print(f"Nameserver: [{line}]")
    
    # MailServer - Düzeltildi
    mx_output = get_mail_servers(site_ad, timeout)
    for line in mx_output.splitlines():
        if "mail is handled by" in line:
            words = line.split()
            if len(words) >= 6:
                # "example.com mail is handled by 10 mail.example.com."
                # Index 5'ten sonrası mail server
                mx_sonuc = ' '.join(words[5:])
                print(f"Mailserver: [{mx_sonuc}]")
        elif "HATA" in line:
            print(f"Mailserver: [{line}]")
        elif "has no MX record" in line:
            print(f"Mailserver: [MX kaydı bulunamadı]")
    
    # IPv4
    ipv4_output = get_ipv4_addresses(site_ad, timeout)
    ipv4_regexli = re.findall(r'(\d+\.\d+\.\d+\.\d+)', ipv4_output)
    if ipv4_regexli:
        print(f"IPv4: [{' , '.join(ipv4_regexli)}]")
    else:
        print(f"IPv4: [HATA: {site_ad}.]")
    
    # HTTP Headers - Düzeltildi
    http_output = get_http_headers(site_ad, timeout)
    
    if "HATA" not in http_output:
        http_bilgisi = re.search(r'HTTP\/[\d.]+\s+(\d+)', http_output)
        server_bilgisi = re.search(r'^Server:\s*(.*)', http_output, re.MULTILINE)
        url_bilgisi = re.search(r'^Location:\s*(.*)', http_output, re.MULTILINE)
        
        if http_bilgisi:
            print(f"HTTP: [{http_bilgisi.group(1).strip()}]")
        else:
            print("HTTP: [HTTP status kodu bulunamadı.]")
        
        if server_bilgisi:
            print(f"Server Info: [{server_bilgisi.group(1).strip()}]")
        else:
            print("Server Info: [Bilgi yok.]")
        
        if url_bilgisi:
            print(f"URL: [{url_bilgisi.group(1).strip()}]")
        else:
            print("URL: [Bilgi yok.]")
    else:
        print("HTTP: [Sunucuya bağlanamadı.]")
        print("Server Info: [Bilgi alınamadı.]")
        print("URL: [Bilgi alınamadı.]")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="whah example.com.")
    parser.add_argument("domain", help="The domain to query")
    args = parser.parse_args()
    main(args.domain)
