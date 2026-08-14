import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("全接口 web 测试", r"""
COOKIE=/tmp/ly_cookie_full.txt
rm -f $COOKIE
echo "===== 1. 登录 ====="
curl -s -X POST "http://127.0.0.1/d/auth" -d "auth_target=login&auth_user=admin&auth_pass=admin" -c $COOKIE --max-time 30
echo ""
echo "===== 2. auth_status ====="
curl -s "http://127.0.0.1/d/auth?auth_target=auth_status" -b $COOKIE --max-time 30
echo ""
echo "===== 3. feature 各类型 ====="
for t in tcpinit dns service ip_scan port_scan sus black mo url_content dga; do
  CNT=$(curl -s "http://127.0.0.1/d/feature?action=get&devid=1&type=$t&starttime=1786596300&endtime=1786603200" -b $COOKIE --max-time 90 2>&1 | grep -c "devid")
  echo "  $t: $CNT 条"
done
echo "===== 4. event / event_aggre ====="
echo -n "event: "; curl -s "http://127.0.0.1/d/event?action=get&devid=1&starttime=1786596300&endtime=1786603200" -b $COOKIE --max-time 60 2>&1 | head -c 100; echo ""
echo -n "event aggre: "; curl -s "http://127.0.0.1/d/event?action=aggre&devid=1&starttime=1786596300&endtime=1786603200" -b $COOKIE --max-time 60 2>&1 | head -c 100; echo ""
echo "===== 5. mo ====="
echo -n "mo get: "; curl -s "http://127.0.0.1/d/mo?op=get&devid=1" -b $COOKIE --max-time 60 2>&1 | grep -c devid; echo " 条"
echo -n "mo gget: "; curl -s "http://127.0.0.1/d/mo?op=gget&devid=1" -b $COOKIE --max-time 60 2>&1 | head -c 150; echo ""
echo "===== 6. config 各类型 ====="
for t in user agent device event mo bwlist internalip internalsrv; do
  echo -n "  $t: "
  curl -s "http://127.0.0.1/d/config?type=$t&op=get" -b $COOKIE --max-time 60 2>&1 | head -c 120
  echo ""
done
echo "===== 7. sctl ====="
curl -s -X POST "http://127.0.0.1/d/sctl" -d "op=status&nodetype=server&servicetype=ssh&id=0" -b $COOKIE --max-time 30 2>&1 | head -c 120
echo ""
echo "===== 8. 其他接口 ====="
echo -n "topn: "; curl -s "http://127.0.0.1/d/topn?action=get&devid=1&starttime=1786596300&endtime=1786603200" -b $COOKIE --max-time 60 2>&1 | head -c 120; echo ""
echo -n "ipinfo: "; curl -s "http://127.0.0.1/d/ipinfo?action=get&ip=10.10.102.100" -b $COOKIE --max-time 60 2>&1 | head -c 120; echo ""
echo -n "portinfo: "; curl -s "http://127.0.0.1/d/portinfo?action=get&port=443" -b $COOKIE --max-time 60 2>&1 | head -c 120; echo ""
echo -n "locinfo: "; curl -s "http://127.0.0.1/d/locinfo?action=get&ip=8.8.8.8" -b $COOKIE --max-time 60 2>&1 | head -c 120; echo ""
echo -n "geoinfo: "; curl -s "http://127.0.0.1/d/geoinfo?action=get&ip=8.8.8.8" -b $COOKIE --max-time 60 2>&1 | head -c 120; echo ""
echo -n "threatinfo: "; curl -s "http://127.0.0.1/d/threatinfo?action=get" -b $COOKIE --max-time 60 2>&1 | head -c 120; echo ""
echo -n "threatinfopro: "; curl -s "http://127.0.0.1/d/threatinfopro?action=get" -b $COOKIE --max-time 60 2>&1 | head -c 120; echo ""
echo -n "evidence: "; curl -s "http://127.0.0.1/d/evidence?action=get&devid=1" -b $COOKIE --max-time 60 2>&1 | head -c 120; echo ""
echo -n "event_feature: "; curl -s "http://127.0.0.1/d/event_feature?action=get&devid=1" -b $COOKIE --max-time 60 2>&1 | head -c 120; echo ""
echo "===== 9. 页面 ====="
curl -s -o /dev/null -w "  /: %{http_code}\n" "http://127.0.0.1/" --max-time 15
curl -s -o /dev/null -w "  /ui/: %{http_code}\n" "http://127.0.0.1/ui/" --max-time 15
echo "===== 10. logout ====="
curl -s -X POST "http://127.0.0.1/d/logout" -b $COOKIE --max-time 30
echo ""
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
