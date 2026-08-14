import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("localStorage 键名", r"""
echo "=== 1. localStorage 相关代码 ==="
grep -o "localStorage[^;]\{0,100\}" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -10
echo ""
echo "=== 2. theme 字符串键 ==="
grep -o "[a-zA-Z_]*[Tt]heme[a-zA-Z_]*[^,;)]\{0,40\}" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | sort -u | head -10
echo ""
echo "=== 3. vendor chunk 中 theme 相关 ==="
grep -o "localStorage[^;]\{0,80\}" /Server/www/ui/static/js/2.2db6edf7.chunk.js 2>/dev/null | grep -i "theme\|color" | head -5
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