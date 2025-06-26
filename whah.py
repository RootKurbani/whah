#!/usr/bin/env python3

import subprocess
import re
import argparse
import time

# host -t ns // NameServer
def get_name_servers(site_ad, timeout):
    try:
        result = subprocess.run(['host', '-t', 'ns', site_ad], capture_output=True, text=True, timeout=timeout)
        return result.stdout
    except subprocess.TimeoutExpired:
        return f"HATA [{site_ad} cevap vermedi.]\n"
    except Exception as e:
        return f"HATA {site_ad}: {e}\n"

# host -t mx // MailServer
def get_mail_servers(site_ad, timeout):
    try:
        result = subprocess.run(['host', '-t', 'mx', site_ad], capture_output=True, text=True, timeout=timeout)
        return result.stdout
    except subprocess.TimeoutExpired:
        return f"HATA [{site_ad} cevap vermedi.]\n"
    except Exception as e:
        return f"HATA {site_ad}: {e}\n"

# host -t cname // CNAME
def get_cname(site_ad, timeout):
    try:
        result = subprocess.run(['host', '-t', 'cname', site_ad], capture_output=True, text=True, timeout=timeout)
        return result.stdout
    except subprocess.TimeoutExpired:
        return f"HATA [{site_ad} cevap vermedi.]\n"
    except Exception as e:
        return f"HATA {site_ad}: {e}\n"

# host -t a // IPv4
def get_ipv4_addresses(site_ad, timeout):
    try:
        result = subprocess.run(['host', '-t', 'a', site_ad], capture_output=True, text=True, timeout=timeout)
        return result.stdout
    except subprocess.TimeoutExpired:
        return f"HATA [{site_ad} cevap vermedi.]\n"
    except Exception as e:
        return f"HATA {site_ad}: {e}\n"

# curl -I // Server Info
def get_http_headers(site_ad, timeout):
    try:
        result = subprocess.run(['curl', '-I', site_ad], capture_output=True, text=True, timeout=timeout)
        return result.stdout
    except subprocess.TimeoutExpired:
        return f"HATA [{site_ad} cevap vermedi.]\n"
    except Exception as e:
        return f"HATA {site_ad}: {e}\n"

def main(site_ad):
    timeout = 5 #00:00:05
    
    # NameServer regex
    ns_output = get_name_servers(site_ad, timeout)
    print(f"\n{site_ad}\n")
    for line in ns_output.splitlines():
        words = line.split()
        if len(words) > 3:
            ns_sonuc = ' '.join(words[3:])
            print(f"Nameserver: [{ns_sonuc}]")
        else:
            print(f"Nameserver: [{line}]")

    # MailServer regex
    mx_output = get_mail_servers(site_ad, timeout)
    for line in mx_output.splitlines():
        words = line.split()
        if len(words) > 3:
            metin_sonuc = ' '.join(words[5:])
            print(f"Mailserver: [{metin_sonuc}]")
        else:
            print(f"Mailserver: [{line}]")

   # Cname regex
    cname_output = get_cname(site_ad, timeout)
    for line in cname_output.splitlines():
        words = line.split()
        if len(words) > 3:
            metin_sonuc = ' '.join(words[5:])
            print(f"Cname: [{metin_sonuc}]")
        else:
            print(f"Cname: [{line}]")


    # IPv4 regex
    ipv4_output = get_ipv4_addresses(site_ad, timeout)
    ipv4_regexli = re.findall(r'(\d+\.\d+\.\d+\.\d+)', ipv4_output)
    if ipv4_regexli:
        print(f"IPv4: [{' , '.join(ipv4_regexli)}]")
    else:
        print(f"IPv4: [HATA: {site_ad}.]")

    # HTTP HEAD regex
    http_output = get_http_headers(site_ad, timeout)
    http_bilgisi = re.search(r'HTTP\/\d+\.\d+\s+(\d+)', http_output, re.MULTILINE)
    server_bilgisi = re.search(r'^Server:\s*(.*)', http_output, re.MULTILINE)
    url_bilgisi = re.search(r'^Location:\s*(.*)', http_output, re.MULTILINE)

    if http_bilgisi:
        print(f"HTTP: [{http_bilgisi.group(1).strip()}]")
    else:
        print("HTTP: [Muhtemel olarak sunucu yok.]")

    if server_bilgisi:
        print(f"Server Info: [{server_bilgisi.group(1).strip()}]")
    else:
        print("Server Info: [Bilgi yok.]")

    if url_bilgisi:
        print(f"URL: [{url_bilgisi.group(1).strip()}]")
    else:
        print("URL: [Bilgi yok.]")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="whah example.com.")
    parser.add_argument("domain", help="The domain to query")
    args = parser.parse_args()

    main(args.domain)
