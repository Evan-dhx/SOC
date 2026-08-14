import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("HTTPS 下完整闭环重测", r"""
echo "===== 1. HTTPS 重新登录 ====="
TOKEN=$(curl -sk -X POST "https://127.0.0.1:8090/api/login" -H "Content-Type: application/json" -d '{"user":"admin","pass":"admin"}' --max-time 5 | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))")
echo -n "登录: "; [ -n "$TOKEN" ] && echo "OK" || echo "FAIL"
echo ""
echo "===== 2. 管理 API（HTTPS） ====="
echo -n "config: "; curl -sk "https://127.0.0.1:8090/api/config" -H "Authorization: Bearer $TOKEN" --max-time 5 | python3 -c "import sys,json; d=json.load(sys.stdin); print('OK, key=' + d['config']['service_key'][:10] + '...')"
echo -n "stats: "; curl -sk "https://127.0.0.1:8090/api/stats" -H "Authorization: Bearer $TOKEN" --max-time 5 | python3 -c "import sys,json; d=json.load(sys.stdin); print('total=' + str(d['total']))"
echo ""
echo "===== 3. 查询端口闭环（HTTP） ====="
SERVICE_KEY=$(curl -sk "https://127.0.0.1:8090/api/config" -H "Authorization: Bearer $TOKEN" --max-time 5 | python3 -c "import sys,json; print(json.load(sys.stdin)['config']['service_key'])")
JWT=$(curl -s -X POST "http://127.0.0.1:8091/apisix/plugin/jwt/sign?key=$SERVICE_KEY" -d "key=$SERVICE_KEY" --max-time 5)
echo -n "命中IP: "; curl -s "http://127.0.0.1:8091/query?ip=185.220.101.34&jwt=$JWT" --max-time 5 | head -c 120
echo ""
echo -n "未命中: "; curl -s "http://127.0.0.1:8091/query?ip=8.8.8.8&jwt=$JWT" --max-time 5
echo ""
echo ""
echo "===== 4. 流影威胁情报闭环 ====="
COOKIE=/tmp/ly_cookie_https2.txt
rm -f $COOKIE
curl -s -X POST "http://127.0.0.1/d/auth" -d "auth_target=login&auth_user=admin&auth_pass=21232f297a57a5a743894a0e4a801fc3" -c $COOKIE --max-time 30 > /dev/null
curl -s -X POST "http://127.0.0.1/d/threatconf" -d "op=save&api_key=&key=$SERVICE_KEY&tic_host=&tic_port=&tisrs_host=127.0.0.1&tisrs_port=8091" -b $COOKIE --max-time 30
echo ""
echo -n "threatinfo 命中: "; curl -s "http://127.0.0.1/d/threatinfo?ip=185.220.101.34" -b $COOKIE --max-time 30 | head -c 120
echo ""
echo -n "threatinfo 未命中: "; curl -s "http://127.0.0.1/d/threatinfo?ip=8.8.8.8" -b $COOKIE --max-time 30
echo ""
echo -n "测试按钮: "; curl -s -X POST "http://127.0.0.1/d/threatconf" -d "op=test" -b $COOKIE --max-time 30
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1500]}")

client.close()