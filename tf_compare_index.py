import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("对比 index.html 三个版本", r"""
echo "=== 1. 当前 index.html（完整） ==="
cat /Server/www/ui/index.html
echo ""
echo ""
echo "=== 2. index.html.bak（17:44 版本） ==="
cat /Server/www/ui/index.html.bak
echo ""
echo ""
echo "=== 3. index.html.full_bak（18:30 版本） ==="
cat /Server/www/ui/index.html.full_bak
echo ""
echo "=== 4. static 目录 JS 是否完整 ==="
ls -la /Server/www/ui/static/js/ 2>/dev/null | head -20
echo ""
echo "=== 5. app-config 目录 ==="
ls -la /Server/www/ui/app-config/ 2>/dev/null
cat /Server/www/ui/app-config/*.js 2>/dev/null | head -30
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