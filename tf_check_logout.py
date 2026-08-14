import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("logout 源码 + extract_event HTTP 测试", r"""
echo "=== 1. logout 相关源码 ==="
find /root/SOC -name "logout*" -type f 2>/dev/null | head -5
echo ""
echo "=== 2. logout 二进制是什么 ==="
file /Server/www/d/logout 2>/dev/null
strings /Server/www/d/logout 2>/dev/null | grep -i "auth\|logout" | head -5
echo ""
echo "=== 3. 测试 10081 extract_event（HTTP） ==="
curl -s -X POST "http://127.0.0.1:10081/extract_event" -d "devid: 1
starttime: 1786596300
endtime: 1786601400" --max-time 60 2>&1 | head -c 500
echo ""
echo "=== 4. 测试 10081 extract_event_feature ==="
curl -s -X POST "http://127.0.0.1:10081/extract_event_feature" -d "devid: 1
starttime: 1786596300
endtime: 1786601400" --max-time 60 2>&1 | head -c 300
echo ""
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=240)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()
