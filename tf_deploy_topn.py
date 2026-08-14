import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("编译部署 topn", r"""
cd /root/SOC/ly_server_src/server
echo "=== 1. 编译 topn ==="
g++ topn.cpp dbc.o -Wall -g -std=c++17 -fpermissive -lpthread -I/usr/local/include -I/usr/include/mysql -I/usr/include/cppdb -I/usr/include/cgicc -I. -I/root/SOC/ly_analyser_src/common -L/usr/lib64 -L/usr/lib -L/usr/local/lib -L/usr/lib64/mysql -L/usr/lib/mysql -L/usr/local/mysql/lib -L../common -lcommon -lcppdb -lcgicc -lcurl -lprotobuf -lmysqlclient -lpthread -ljson-c -lboost_regex -o topn 2>&1 | head -5
echo "编译退出码: $?"
ls -la topn
echo ""
echo "=== 2. 符号检查 ==="
LD_LIBRARY_PATH=/Agent/lib:/Server/lib:/usr/local/lib ldd -r topn 2>&1 | grep -c "undefined" || echo "0 undefined"
echo ""
echo "=== 3. 部署 + 全量重测 ==="
cp topn /Server/www/d/topn
chmod 755 /Server/www/d/topn
COOKIE=/tmp/ly_cookie_topn2.txt
rm -f $COOKIE
curl -s -X POST "http://127.0.0.1/d/auth" -d "auth_target=login&auth_user=admin&auth_pass=admin" -c $COOKIE --max-time 30 >/dev/null
echo -n "topn: "
curl -s "http://127.0.0.1/d/topn?action=get&devid=1&starttime=1786596300&endtime=1786603200" -b $COOKIE --max-time 90 2>&1 | head -c 300
echo ""
echo ""
echo "=== 4. 全部接口回归（含之前异常的） ==="
echo -n "ipinfo: "; curl -s "http://127.0.0.1/d/ipinfo?action=get&ip=10.10.102.100" -b $COOKIE --max-time 60 2>&1 | head -c 150; echo ""
echo -n "geoinfo: "; curl -s "http://127.0.0.1/d/geoinfo?action=get&ip=8.8.8.8" -b $COOKIE --max-time 60 2>&1 | head -c 150; echo ""
echo -n "locinfo: "; curl -s "http://127.0.0.1/d/locinfo?action=get&iplist=8.8.8.8" -b $COOKIE --max-time 60 2>&1 | head -c 150; echo ""
echo -n "feature tcpinit: "; curl -s "http://127.0.0.1/d/feature?action=get&devid=1&type=tcpinit&starttime=1786596300&endtime=1786603200" -b $COOKIE --max-time 90 2>&1 | grep -c devid; echo " 条"
echo -n "mo: "; curl -s "http://127.0.0.1/d/mo?op=get&devid=1" -b $COOKIE --max-time 60 2>&1 | grep -c devid; echo " 条"
echo -n "event: "; curl -s "http://127.0.0.1/d/event?action=get&devid=1&starttime=1786596300&endtime=1786603200" -b $COOKIE --max-time 60 2>&1 | head -c 100; echo ""
echo -n "config: "; curl -s "http://127.0.0.1/d/config?type=user&op=get" -b $COOKIE --max-time 60 2>&1 | head -c 100; echo ""
echo -n "sctl: "; curl -s -X POST "http://127.0.0.1/d/sctl" -d "op=status&nodetype=server&servicetype=ssh&id=0" -b $COOKIE --max-time 30 2>&1 | head -c 100; echo ""
echo ""
echo "=== 5. 最新错误日志 ==="
tail -5 /var/log/httpd/ly_error_log 2>/dev/null | grep -v "AH00489\|AH00094\|AH02282\|AH01232\|AH00492\|suexec\|mpm_event"
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=600)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()