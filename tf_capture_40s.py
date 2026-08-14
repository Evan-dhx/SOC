import paramiko
import sys
import time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Capture loopback 9995 for 40 seconds while generating traffic
print("[抓包 lo:9995 40 秒（覆盖 30 秒导出周期）]")
stdin, stdout, stderr = client.exec_command(
    "timeout 40 tcpdump -i lo -c 100 udp port 9995 2>&1", timeout=60)
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
print(f"=== tcpdump lo:9995 结果 ===\n{out}")

# Check nfcapd file
stdin, stdout, stderr = client.exec_command(
    "stat -c '%s bytes %y' /data/flow/nfcapd.current; ls -la /data/flow/ | tail -4", timeout=30)
print(f"\n=== nfcapd.current ===\n{stdout.read().decode('utf-8', errors='replace')}")

# Check tsensor journal for export activity
stdin, stdout, stderr = client.exec_command(
    "journalctl -u tsensor --no-pager --since '5 minutes ago' 2>/dev/null | grep -vE 'pattern|plugin|Welcome' | tail -10", timeout=30)
print(f"\n=== tsensor 最近日志 ===\n{stdout.read().decode('utf-8', errors='replace')}")

client.close()
