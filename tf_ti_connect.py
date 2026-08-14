import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

sftp = client.open_sftp()
sftp.put(r'd:\QorderProject\SOC\ti_server\server.py', '/opt/ti_server/server.py')
sftp.close()
print("server.py 已更新")

cmds = [
    ("重启 + 流影对接闭环测试", r"""
echo "=== 1. 重启 ti_server ==="
systemctl restart ti-server
sleep 2
systemctl is-active ti-server
echo ""
echo "=== 2. 根路径兼容自测 ==="
curl -s -o /dev/null -w "GET / (无jwt,管理界面): %{http_code}\n" "http://127.0.0.1:8090/" --max-time 5
TOKEN=$(curl -s -X POST "http://127.0.0.1:8090/api/login" -H "Content-Type: application/json" -d '{"user":"admin","pass":"admin"}' --max-time 5 | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))")
SERVICE_KEY=$(curl -s "http://127.0.0.1:8090/api/config" -H "Authorization: Bearer $TOKEN" --max-time 5 | python3 -c "import sys,json; print(json.load(sys.stdin)['config']['service_key'])")
JWT=$(curl -s -X POST "http://127.0.0.1:8090/apisix/plugin/jwt/sign?key=$SERVICE_KEY" -d "key=$SERVICE_KEY" --max-time 5 | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))")
echo -n "POST / (查询): "; curl -s -X POST "http://127.0.0.1:8090/?ip=185.220.101.34&jwt=$JWT" --max-time 5 | head -c 150
echo ""
echo ""

echo "=== 3. 流影登录 ==="
COOKIE=/tmp/ly_cookie_conn.txt
rm -f $COOKIE
curl -s -X POST "http://127.0.0.1/d/auth" -d "auth_target=login&auth_user=admin&auth_pass=21232f297a57a5a743894a0e4a801fc3" -c $COOKIE --max-time 30
echo ""

echo ""
echo "=== 4. 流影 threatconf 配置指向 ti_server ==="
curl -s -X POST "http://127.0.0.1/d/threatconf" -d "op=save&api_key=&key=$SERVICE_KEY&tic_host=&tic_port=&tisrs_host=127.0.0.1&tisrs_port=8090" -b $COOKIE --max-time 30
echo ""

echo ""
echo "=== 5. 核心闭环：流影 threatinfo 走 ti_server 真实后端 ==="
echo -n "命中(185.220.101.34): "; curl -s "http://127.0.0.1/d/threatinfo?ip=185.220.101.34" -b $COOKIE --max-time 30
echo ""
echo -n "命中域名(evil-c2): "; curl -s "http://127.0.0.1/d/threatinfo?domain=evil-c2.example.com" -b $COOKIE --max-time 30
echo ""
echo -n "未命中(8.8.8.8): "; curl -s "http://127.0.0.1/d/threatinfo?ip=8.8.8.8" -b $COOKIE --max-time 30
echo ""

echo ""
echo "=== 6. 测试按钮（op=test） ==="
curl -s -X POST "http://127.0.0.1/d/threatconf" -d "op=test" -b $COOKIE --max-time 30
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()