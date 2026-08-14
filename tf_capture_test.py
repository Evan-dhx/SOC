import paramiko
import sys
import time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Install tcpdump and check tsensor service", r"""
echo "=== 1. tsensor.service 配置 ==="
cat /etc/systemd/system/tsensor.service
echo ""
echo "=== 2. 安装 tcpdump ==="
which tcpdump || yum install -y tcpdump 2>&1 | tail -2
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

# Capture loopback 9995 while generating traffic from Windows
print("\n[抓包 127.0.0.1:9995 + Windows 制造流量]")
stdin, stdout, stderr = client.exec_command(
    "timeout 15 tcpdump -i lo -c 50 udp port 9995 2>&1", timeout=30)
time.sleep(1)

import urllib.request
ok = 0
for i in range(50):
    try:
        r = urllib.request.urlopen('http://10.10.102.220/', timeout=5)
        r.read()
        ok += 1
    except Exception as e:
        pass
    time.sleep(0.2)
print(f"HTTP 请求成功 {ok}/50")

out = stdout.read().decode('utf-8', errors='replace')
print(f"\n=== tcpdump 结果 ===\n{out}")

# Also capture ens192 to see if tsensor sees the traffic
print("\n[抓包 ens192（看流量是否经过网卡）]")
stdin, stdout, stderr = client.exec_command(
    "timeout 10 tcpdump -i ens192 -c 30 tcp port 80 2>&1", timeout=30)
time.sleep(1)
for i in range(30):
    try:
        r = urllib.request.urlopen('http://10.10.102.220/', timeout=5)
        r.read()
    except Exception:
        pass
    time.sleep(0.2)
out = stdout.read().decode('utf-8', errors='replace')
print(f"\n=== ens192 tcpdump 结果 ===\n{out}")

client.close()
