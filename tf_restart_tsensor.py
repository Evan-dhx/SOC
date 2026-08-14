import paramiko
import sys
import time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Check tsensor threads before restart", r"""
echo "=== 1. tsensor 线程数（当前实例） ==="
cat /proc/$(pidof tsensor)/status 2>/dev/null | grep -E "Threads|State"
ls /proc/$(pidof tsensor)/task/ 2>/dev/null | wc -l
echo ""
echo "=== 2. 重启 tsensor ==="
systemctl restart tsensor
sleep 5
echo "重启完成"
systemctl status tsensor 2>&1 | head -8
echo ""
echo "=== 3. 新 PID 和线程 ==="
NEWPID=$(pidof tsensor)
echo "New PID: $NEWPID"
cat /proc/$NEWPID/status | grep -E "Threads|State"
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

# Now capture 9995 while generating traffic
print("\n[重启后抓包 9995 + 制造流量]")
stdin, stdout, stderr = client.exec_command(
    "timeout 15 tcpdump -i lo -c 30 udp port 9995 2>&1", timeout=30)
time.sleep(1)

import urllib.request
ok = 0
for i in range(50):
    try:
        r = urllib.request.urlopen('http://10.10.102.220/', timeout=5)
        r.read()
        ok += 1
    except Exception:
        pass
    time.sleep(0.2)
print(f"HTTP 请求成功 {ok}/50")

out = stdout.read().decode('utf-8', errors='replace')
print(f"\n=== tcpdump lo:9995 结果 ===\n{out}")

# Check nfcapd file growth
stdin, stdout, stderr = client.exec_command("stat -c '%s bytes %y' /data/flow/nfcapd.current", timeout=30)
print(f"\n=== nfcapd.current ===\n{stdout.read().decode('utf-8', errors='replace')}")

client.close()
