import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("隐藏能力描述文字", r"""
cd /Server/www/ui
echo "=== 1. 备份 ==="
cp index.html index.html.tech_bak2
echo "已备份 index.html.tech_bak2"
echo ""
echo "=== 2. 追加隐藏规则到注入样式 ==="
python3 - <<'PYEOF'
src = open('/Server/www/ui/index.html').read()
rule = '''
/* 隐藏左侧能力描述文字（只保留标题） */
.login-left-center-item .item-text { display: none !important; }
.login-left-center-item { margin-bottom: 34px !important; }
'''
marker = '</style>'
hide_rule = '.login-left-center-item .item-text { display: none !important; }'
if hide_rule in src:
    print("隐藏规则已存在，跳过")
else:
    pos = src.find(marker)
    if pos < 0:
        print("未找到 style 结束标记")
    else:
        # 在第一个 </style> 前插入（ly-tech-login-style 块）
        src = src[:pos] + rule + src[pos:]
        open('/Server/www/ui/index.html', 'w').write(src)
        print("已追加隐藏规则")
PYEOF
echo ""
echo "=== 3. 验证 ==="
grep -c "item-text" /Server/www/ui/index.html
echo ""
echo "=== 4. 页面响应 ==="
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