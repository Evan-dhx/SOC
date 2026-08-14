import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

FIX_RULE = '''
/* ========== 修复嵌套矩形：内层 input 去边框 ========== */
.login-form .ant-input-affix-wrapper .ant-input,
.login-form .ant-input-affix-wrapper .ant-input:hover {
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
}
.login-form .ant-input-affix-wrapper {
    background: rgba(3, 14, 30, 0.9) !important;
    border: 1px solid rgba(0, 229, 255, 0.28) !important;
    border-radius: 8px !important;
}
.login-form .ant-input-affix-wrapper:focus-within {
    border-color: #00e5ff !important;
    box-shadow: 0 0 0 1px rgba(0, 229, 255, 0.35), 0 0 18px rgba(0, 229, 255, 0.25) !important;
}
.login-form .ant-input-prefix,
.login-form .ant-input-suffix {
    color: rgba(0, 229, 255, 0.75) !important;
}
'''

cmds = [
    ("修复嵌套矩形", f"""
cd /Server/www/ui
echo "=== 1. 备份 ==="
cp index.html index.html.input_fix_bak
echo "已备份 index.html.input_fix_bak"
echo ""
echo "=== 2. 追加修复规则 ==="
python3 - <<'PYEOF'
src = open('/Server/www/ui/index.html').read()
fix = {FIX_RULE!r}
marker = '修复嵌套矩形'
if marker in src:
    print('修复规则已存在，跳过')
else:
    pos = src.find('</style>')
    if pos < 0:
        print('未找到 style 结束标记')
    else:
        src = src[:pos] + fix + src[pos:]
        open('/Server/www/ui/index.html', 'w').write(src)
        print('修复规则已追加')
PYEOF
echo ""
echo "=== 3. 验证 ==="
grep -c "修复嵌套矩形" index.html
echo ""
echo "=== 4. 页面响应 ==="
curl -s -o /dev/null -w "/ui/: %{{http_code}}\\n" "http://127.0.0.1/ui/" --max-time 15
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