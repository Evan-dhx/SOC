import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Apache 配置 + 域名访问测试", r"""
echo "=== 1. ly_server.conf 当前内容 ==="
cat /etc/httpd/conf.d/ly_server.conf
echo ""
echo "=== 2. 域名方式完整链路（模拟浏览器） ==="
COOKIE=/tmp/ly_cookie_domain.txt
rm -f $COOKIE
curl -s -X POST "http://10.10.102.220/d/auth" -d "auth_target=login&auth_user=admin&auth_pass=21232f297a57a5a743894a0e4a801fc3" -c $COOKIE --max-time 30 2>&1
echo ""
echo "--- cookie ---"
cat $COOKIE 2>/dev/null | grep -v "^#"
echo ""
echo -n "feature: "; curl -s "http://10.10.102.220/d/feature?action=get&devid=1&type=tcpinit&starttime=1786596300&endtime=1786603200" -b $COOKIE --max-time 60 2>&1 | head -c 100; echo ""
echo -n "auth_status: "; curl -s "http://10.10.102.220/d/auth?auth_target=auth_status" -b $COOKIE --max-time 30 2>&1; echo ""
echo ""
echo "=== 3. 无 cookie 访问（应被拒） ==="
curl -s "http://10.10.102.220/d/feature?action=get&devid=1&type=tcpinit&starttime=1786596300&endtime=1786603200" --max-time 60 2>&1 | head -c 150
echo ""
echo ""
echo "=== 4. 前端'未登录'提示逻辑（编译版 JS 搜索） ==="
grep -c "未登录" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null
grep -o "未登录[^\"']*" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -3
echo ""
echo "=== 5. auth.cpp 转发逻辑中 session 检查 ==="
grep -n -B3 -A10 "未登录\|not login\|NOT_LOGIN\|auth_target\|popen\|forward" /root/SOC/ly_server_src/server/auth.cpp | head -50
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