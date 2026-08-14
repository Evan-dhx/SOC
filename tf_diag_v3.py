import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("诊断当前 index.html", r"""
cd /Server/www/ui
echo "=== 1. 文件清单与时间 ==="
ls -la index.html* | awk '{print $6, $7, $8, $9}'
echo ""
echo "=== 2. 当前 index.html 注入标记检查 ==="
echo -n "ly-tech-login-style: "; grep -c "ly-tech-login-style" index.html
echo -n "ly-net-anim: "; grep -c "ly-net-anim" index.html
echo -n "ly-brand-rename: "; grep -c "ly-brand-rename" index.html
echo -n "item-text hide: "; grep -c "item-text { display: none" index.html
echo -n "天网: "; grep -c "天网" index.html
echo -n "login-title-logo hide: "; grep -c "login-title-logo > :last-child" index.html
echo ""
echo "=== 3. 当前 index.html 大小 ==="
wc -c index.html
echo ""
echo "=== 4. 干净的 .bak 是否可用 ==="
wc -c index.html.bak 2>/dev/null
grep -c "ly-tech-login-style" index.html.bak 2>/dev/null
echo ""
echo "=== 5. 页面实际返回的 body 开头 ==="
curl -s "http://127.0.0.1/ui/" --max-time 15 2>&1 | python3 -c "import sys; s=sys.stdin.read(); i=s.find('<body>'); print(s[i:i+300] if i>0 else s[:300])"
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