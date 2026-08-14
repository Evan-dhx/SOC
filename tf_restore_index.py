import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("恢复 index.html", r"""
echo "=== 1. 备份当前坏掉的 index.html ==="
cp /Server/www/ui/index.html /Server/www/ui/index.html.broken
echo "已备份为 index.html.broken"
echo ""
echo "=== 2. 恢复为 17:44 完整版（index.html.bak） ==="
cp /Server/www/ui/index.html.bak /Server/www/ui/index.html
echo "已恢复"
echo ""
echo "=== 3. 验证恢复后内容 ==="
cat /Server/www/ui/index.html | head -c 400
echo ""
echo "..."
echo ""
echo "=== 4. 页面响应 ==="
curl -s -o /dev/null -w "/ui/: %{http_code}\n" "http://127.0.0.1/ui/" --max-time 15
curl -s "http://127.0.0.1/ui/" --max-time 15 2>&1 | grep -o "static/js/[a-z0-9.]*\.js" | head -5
echo ""
echo "=== 5. JS 文件可访问性 ==="
for f in runtime-main.70783980.js 2.2db6edf7.chunk.js main.ff156c89.chunk.js; do
  curl -s -o /dev/null -w "  $f: %{http_code}\n" "http://127.0.0.1/ui/static/js/$f" --max-time 15
done
echo ""
echo "=== 6. 登录验证 ==="
curl -s -X POST "http://127.0.0.1/d/auth" -d "auth_target=login&auth_user=admin&auth_pass=21232f297a57a5a743894a0e4a801fc3" --max-time 30 2>&1
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