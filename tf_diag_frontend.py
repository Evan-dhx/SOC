import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("前端位置 + auth 源码", r"""
echo "=== 1. ly_server.conf 完整 ==="
cat /etc/httpd/conf.d/ly_server.conf
echo ""
echo "=== 2. 前端 index.html 位置 ==="
find / -name "index.html" -path "*www*" 2>/dev/null | grep -v "/usr/share" | head -5
find / -name "index.html" -path "*vis*" 2>/dev/null | head -5
find /Server -maxdepth 2 -type d 2>/dev/null | head -20
echo ""
echo "=== 3. auth.cpp 中 getenv 用法 ==="
grep -n "getenv" /root/SOC/ly_server_src/server/auth.cpp | head -10
echo ""
echo "=== 4. auth.cpp 前 80 行 ==="
sed -n '1,80p' /root/SOC/ly_server_src/server/auth.cpp
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
