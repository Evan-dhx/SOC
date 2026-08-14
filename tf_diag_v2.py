import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("诊断当前状态", r"""
echo "=== 1. index.html 是否含我们的注入 ==="
grep -c "ly-tech-login-style" /Server/www/ui/index.html
grep -c "ly-net-anim" /Server/www/ui/index.html
echo ""
echo "=== 2. index.html 修改时间 ==="
ls -la /Server/www/ui/index.html* 2>/dev/null | awk '{print $6, $7, $8, $9}'
echo ""
echo "=== 3. CSS 文件是否被改 ==="
ls -la /Server/www/ui/static/css/ | awk '{print $6, $7, $8, $9}'
echo ""
echo "=== 4. body 背景相关（原 CSS 中 login-page 定义） ==="
grep -o "login-page{[^}]*}" /Server/www/ui/static/css/main.c025dfb1.chunk.css 2>/dev/null | head -c 400
echo ""
echo "=== 5. 注入的 style 是否完整（前 200 字符 + 结尾） ==="
python3 - <<'PYEOF'
src = open('/Server/www/ui/index.html').read()
i = src.find('ly-tech-login-style')
j = src.find('</style>', i)
print("style 块长度:", j - i if i > 0 and j > 0 else "未找到")
print("style 开头:", src[i:i+80] if i > 0 else "")
print("script 存在:", 'ly-net-anim' in src)
k = src.find('ly-net-anim')
print("script 上下文:", src[k:k+120] if k > 0 else "")
PYEOF
echo ""
echo "=== 6. 无痕请求模拟（看服务器实际返回的完整 head 后 1000 字符） ==="
curl -s "http://127.0.0.1/ui/" --max-time 15 2>&1 | python3 -c "import sys; src=sys.stdin.read(); print(src[src.find('</title>'):src.find('</head>')][:800])"
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