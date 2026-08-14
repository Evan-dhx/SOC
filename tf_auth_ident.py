import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("auth_control ident 函数", r"""
echo "=== 1. ident 函数（370-430） ==="
sed -n '370,430p' /root/SOC/ly_server_src/server/auth.cpp
echo ""
echo "=== 2. 前端 qi 函数定义 ==="
grep -o "qi=[^,;]*function[^}]*}" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -c 500
grep -o "function qi[^}]*}" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -c 500
echo ""
echo "=== 3. auth_target 附近上下文 ==="
grep -o ".\{200\}auth_target.\{300\}" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -c 800
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
