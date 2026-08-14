import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("主题存储机制", r"""
echo "=== 1. 编译 JS 中 ThemeParams 键名 ==="
grep -o "setThemeParams[^}]\{0,120\}" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -3
echo ""
echo "=== 2. localStorage 键名线索 ==="
grep -o "getItem([^)]\{0,60\}" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | grep -i "theme\|color" | head -5
echo ""
echo "=== 3. theme link 处理逻辑 ==="
grep -o "getElementById('theme')[^;]\{0,80\}" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -5
echo ""
echo "=== 4. theme css 文件 ==="
ls -la /Server/www/ui/theme/ 2>/dev/null
echo ""
echo "=== 5. dark/light css 变量定义（前 40 行） ==="
head -40 /Server/www/ui/theme/dark.css 2>/dev/null
echo "---light---"
head -40 /Server/www/ui/theme/light.css 2>/dev/null
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