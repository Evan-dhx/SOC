import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("修复粒子动画选择器", r"""
cd /Server/www/ui
echo "=== 1. 备份 ==="
cp index.html index.html.anim_fix_bak
echo "已备份 index.html.anim_fix_bak"
echo ""
echo "=== 2. 替换动画脚本中的登录页选择器 ==="
python3 - <<'PYEOF'
src = open('/Server/www/ui/index.html').read()
# 修复 CSS modules 哈希类名匹配问题：.login-page -> [class*="login-page"]
old_sel = "document.querySelector('.login-page')"
new_sel = 'document.querySelector(\'[class*="login-page"]\')'
if old_sel in src:
    src = src.replace(old_sel, new_sel)
    open('/Server/www/ui/index.html', 'w').write(src)
    print("选择器已修复")
else:
    print("未找到目标选择器（可能已修复）")
# 验证
print("修复后包含:", '[class*="login-page"]' in src)
print("残留旧选择器:", '.login-page\')' in src)
PYEOF
echo ""
echo "=== 3. 页面响应 ==="
curl -s -o /dev/null -w "/ui/: %{http_code}\n" "http://127.0.0.1/ui/" --max-time 15
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