import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("check_user_pass 密码比较", r"""
echo "=== 1. check_user_pass 205-235 ==="
sed -n '205,235p' /root/SOC/ly_server_src/server/auth.cpp
echo ""
echo "=== 2. 前端 md5 用法 ==="
grep -o "md5[^)]*" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -3
grep -c "auth_target" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null
echo ""
echo "=== 3. 前端 auth 请求片段 ==="
grep -o "auth_target[^,;)]*" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -5
grep -o "auth_pass[^,;)]*" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -5
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
