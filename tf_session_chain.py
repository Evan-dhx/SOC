import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("登录后 session 链路测试", r"""
COOKIE=/tmp/ly_cookie_sess.txt
rm -f $COOKIE
echo "=== 1. 登录（前端方式 md5(admin)） ==="
curl -s -X POST "http://127.0.0.1/d/auth" -d "auth_target=login&auth_user=admin&auth_pass=21232f297a57a5a743894a0e4a801fc3" -c $COOKIE --max-time 30 2>&1
echo ""
echo "--- cookie 内容 ---"
cat $COOKIE
echo ""
echo "=== 2. auth_status（带 cookie） ==="
curl -s "http://127.0.0.1/d/auth?auth_target=auth_status" -b $COOKIE --max-time 30 2>&1
echo ""
echo "=== 3. 各接口带 cookie 访问 ==="
echo -n "  feature: "; curl -s "http://127.0.0.1/d/feature?action=get&devid=1&type=tcpinit&starttime=1786596300&endtime=1786603200" -b $COOKIE --max-time 60 2>&1 | head -c 120; echo ""
echo -n "  config: "; curl -s "http://127.0.0.1/d/config?type=user&op=get" -b $COOKIE --max-time 60 2>&1 | head -c 120; echo ""
echo -n "  mo: "; curl -s "http://127.0.0.1/d/mo?op=get&devid=1" -b $COOKIE --max-time 60 2>&1 | head -c 120; echo ""
echo -n "  event: "; curl -s "http://127.0.0.1/d/event?action=get&devid=1&starttime=1786596300&endtime=1786603200" -b $COOKIE --max-time 60 2>&1 | head -c 120; echo ""
echo ""
echo "=== 4. auth.cpp session 校验逻辑（check_session） ==="
grep -n -A25 "static int check_session" /root/SOC/ly_server_src/server/auth.cpp | head -35
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