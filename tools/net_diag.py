import os
import sys
import socket

print('=== Connectivity Diagnostic ===')
print('Python:', sys.version)

# Show proxy/SSL env
for k in ['HTTP_PROXY','HTTPS_PROXY','NO_PROXY','REQUESTS_CA_BUNDLE','SSL_CERT_FILE']:
    print(f'{k}={os.environ.get(k)}')

hosts = [
    'www.google.com',
    'httpbin.org',
    'api.groq.com',
    'generativelanguage.googleapis.com',
]

print('\nDNS:')
for h in hosts:
    try:
        ip = socket.gethostbyname(h)
        print(f'  OK {h} -> {ip}')
    except Exception as e:
        print(f'  FAIL {h}: {e.__class__.__name__}: {e}')

print('\nTCP 443:')
for h in hosts:
    try:
        with socket.create_connection((h, 443), timeout=4):
            print(f'  OK {h}:443')
    except Exception as e:
        print(f'  FAIL {h}:443 -> {e.__class__.__name__}: {e}')

try:
    import requests
except Exception as e:
    print('\nrequests not available:', e)
    requests = None

endpoints = [
    ('google_204','https://www.google.com/generate_204'),
    ('httpbin_200','https://httpbin.org/status/200'),
    ('groq_base','https://api.groq.com'),
    ('gemini_base','https://generativelanguage.googleapis.com'),
]

if requests:
    print('\nHTTPS (verify=True/False):')
    for name, url in endpoints:
        for verify in (True, False):
            try:
                r = requests.get(url, timeout=6, verify=verify)
                print(f'  {name} verify={verify}: HTTP {r.status_code}')
            except Exception as e:
                print(f'  {name} verify={verify}: FAIL {e.__class__.__name__}: {e}')

print('\n=== End Diagnostic ===')
