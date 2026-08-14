import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("验证 mo 新增/删除", r"""
COOKIE=/tmp/ly_cookie5.txt
rm -f $COOKIE
curl -s -X POST "http://127.0.0.1/d/auth" -d "auth_target=login&auth_user=admin&auth_pass=admin" -c $COOKIE --max-time 30 >/dev/null
echo "=== 1. 新增追踪策略（op=add） ==="
curl -s "http://127.0.0.1/d/mo?op=add&devid=1&moip=192.168.1.1&moport=8080&desc=test_web&tag=test&mogroupid=4&direction=ALL" -b $COOKIE --max-time 60 2>&1 | head -c 300
echo ""
echo ""
echo "=== 2. 确认新增（查最新一条） ==="
curl -s "http://127.0.0.1/d/mo?op=get&devid=1" -b $COOKIE --max-time 60 2>&1 | tail -c 400
echo ""
echo ""
echo "=== 3. 删除（op=del&moid=33） ==="
curl -s "http://127.0.0.1/d/mo?op=del&devid=1&moid=33" -b $COOKIE --max-time 60 2>&1 | head -c 300
echo ""
echo ""
echo "=== 4. 确认删除后总数 ==="
curl -s "http://127.0.0.1/d/mo?op=get&devid=1" -b $COOKIE --max-time 60 2>&1 | grep -c "devid"
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
