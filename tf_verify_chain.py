import paramiko
import sys
import time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Capture 9995 while generating traffic (40s covers export cycle)
print("[抓包 lo:9995 45 秒 + 制造流量]")
stdin, stdout, stderr = client.exec_command(
    "timeout 45 tcpdump -i lo -c 50 udp port 9995 2>&1", timeout=70)
time.sleep(2)

import urllib.request
for i in range(100):
    try:
        r = urllib.request.urlopen('http://10.10.102.220/', timeout=5)
        r.read()
    except Exception:
        pass
    time.sleep(0.3)

out = stdout.read().decode('utf-8', errors='replace')
print(f"=== tcpdump lo:9995 ===\n{out}")

# Check nfcapd logs and file
stdin, stdout, stderr = client.exec_command(
    "journalctl --no-pager --since '2 minutes ago' 2>/dev/null | grep -iE 'nfcapd|flowset' | tail -8; echo '---'; stat -c '%s bytes %y' /data/flow/nfcapd.current; ls -la /data/flow/ | tail -5", timeout=30)
print(f"\n=== nfcapd 日志与文件 ===\n{stdout.read().decode('utf-8', errors='replace')}")

client.close()
