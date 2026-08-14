import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("登录页主题状态检查", r"""
cd /Server/www/ui
echo "=== 1. #theme link 当前 href ==="
grep -o 'id="theme"[^>]*' index.html
echo ""
echo "=== 2. 注入的 body 强制深色是否在 ==="
grep -c "body, #root" index.html
grep -o "body, #root[^}]*}" index.html | head -1
echo ""
echo "=== 3. .login-page 背景强制 ==="
grep -o "\.login-page {[^}]*}" index.html | head -1
echo ""
echo "=== 4. theme css 是否被登录页加载 ==="
grep -c "theme/dark.css\|theme/light.css" index.html
echo ""
echo "=== 5. 页面实际返回确认 ==="
curl -s "http://127.0.0.1/ui/" --max-time 15 2>&1 | grep -o 'id="theme"[^>]*'
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