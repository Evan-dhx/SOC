import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("带完整参数测试 config", r"""
echo "=== 1. 登录拿 cookie ==="
COOKIE=/tmp/ly_cookie2.txt
rm -f $COOKIE
curl -s -X POST "http://127.0.0.1/d/auth" -d "auth_target=login&auth_user=admin&auth_pass=admin" -c $COOKIE --max-time 30 >/dev/null
cat $COOKIE | grep SESSION_ID | head -1
echo ""
echo "=== 2. config type=user（带 cookie） ==="
curl -s "http://127.0.0.1/d/config?type=user&op=get" -b $COOKIE --max-time 60 2>&1 | head -c 500
echo ""
echo ""
echo "=== 3. config type=bwlist（带 target） ==="
curl -s "http://127.0.0.1/d/config?type=bwlist&op=get&target=blacklist" -b $COOKIE --max-time 60 2>&1 | head -c 300
echo ""
curl -s "http://127.0.0.1/d/config?type=bwlist&op=get&target=whitelist" -b $COOKIE --max-time 60 2>&1 | head -c 300
echo ""
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=400)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()
