import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("前端文件 + auth 崩溃点", r"""
echo "=== 1. /Server/www 内容 ==="
ls -la /Server/www/ 2>/dev/null
echo ""
echo "=== 2. /Server/www/ui 内容 ==="
ls /Server/www/ui/ 2>/dev/null | head -20
echo ""
echo "=== 3. 找 dist 前端 ==="
find /Server /root/SOC -maxdepth 4 -name "*.html" 2>/dev/null | grep -v node_modules | head -10
echo ""
echo "=== 4. auth.cpp getenv/cookie 部分 ==="
grep -n "getenv\|cookie\|Cookie\|sid\|SESSION" /root/SOC/ly_server_src/server/auth.cpp | head -30
echo ""
echo "=== 5. auth.cpp main 函数 ==="
grep -n "int main" /root/SOC/ly_server_src/server/auth.cpp
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
