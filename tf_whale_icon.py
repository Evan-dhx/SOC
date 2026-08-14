import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# 上传鲸鱼 favicon + 更新版本号
sftp = client.open_sftp()
sftp.put(r'd:\QorderProject\SOC\favicon.svg', '/Server/www/ui/favicon.svg')
sftp.close()
print("鲸鱼 favicon.svg 已上传")

cmds = [
    ("favicon 版本号更新", r"""
cd /Server/www/ui
echo "=== 1. 备份 ==="
cp index.html index.html.whale_icon_bak
echo "已备份 index.html.whale_icon_bak"
echo ""
echo "=== 2. 更新 favicon 版本号（v2 → v3） ==="
python3 - <<'PYEOF'
src = open('/Server/www/ui/index.html').read()
if 'favicon.svg?v=3' in src:
    print('版本号已是最新')
else:
    src = src.replace('favicon.svg?v=2', 'favicon.svg?v=3')
    open('/Server/www/ui/index.html', 'w').write(src)
    print('已更新为 v3')
PYEOF
echo ""
echo "=== 3. 验证 favicon 内容（鲸鱼） ==="
head -c 400 /Server/www/ui/favicon.svg
echo ""
echo ""
echo "=== 4. 页面响应 ==="
curl -s -o /dev/null -w "/ui/: %{http_code}\n" "http://127.0.0.1/ui/" --max-time 15
curl -s -o /dev/null -w "favicon.svg: %{http_code}\n" "http://127.0.0.1/ui/favicon.svg?v=3" --max-time 15
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()