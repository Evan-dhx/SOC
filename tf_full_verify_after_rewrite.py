import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("带 cookie 全接口验证", r"""
echo "=== 1. 登录 ==="
COOKIE=/tmp/ly_cookie4.txt
rm -f $COOKIE
curl -s -X POST "http://127.0.0.1/d/auth" -d "auth_target=login&auth_user=admin&auth_pass=admin" -c $COOKIE --max-time 30 2>&1 | head -c 100
echo ""
echo ""
echo "=== 2. config type=user（关键验证） ==="
curl -s "http://127.0.0.1/d/config?type=user&op=get" -b $COOKIE --max-time 60 2>&1 | head -c 800
echo ""
echo ""
echo "=== 3. config type=event ==="
curl -s "http://127.0.0.1/d/config?type=event&op=get" -b $COOKIE --max-time 60 2>&1 | head -c 300
echo ""
echo ""
echo "=== 4. feature tcpinit ==="
curl -s "http://127.0.0.1/d/feature?action=get&devid=1&type=tcpinit&starttime=1786596300&endtime=1786601400" -b $COOKIE --max-time 90 2>&1 | head -c 300
echo ""
echo ""
echo "=== 5. event / mo / sctl / internalip ==="
echo -n "event: "; curl -s "http://127.0.0.1/d/event?action=get&devid=1&starttime=1786596300&endtime=1786601400" -b $COOKIE --max-time 60 2>&1 | head -c 150; echo ""
echo -n "mo: "; curl -s "http://127.0.0.1/d/mo?op=get&devid=1" -b $COOKIE --max-time 60 2>&1 | head -c 150; echo ""
echo -n "sctl: "; curl -s -X POST "http://127.0.0.1/d/sctl" -d "op=status&nodetype=server&servicetype=ssh&id=0" -b $COOKIE --max-time 30 2>&1 | head -c 150; echo ""
echo -n "internalip: "; curl -s "http://127.0.0.1/d/config?type=internalip&op=get" -b $COOKIE --max-time 30 2>&1 | head -c 150; echo ""
echo ""
echo "=== 6. 错误密码登录（安全验证） ==="
curl -s -X POST "http://127.0.0.1/d/auth" -d "auth_target=login&auth_user=admin&auth_pass=wrong" --max-time 30 2>&1 | head -c 100
echo ""
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=500)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()
