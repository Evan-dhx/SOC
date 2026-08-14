import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("HTTPS 全流程测试", r"""
echo "===== 1. 生成自签 PFX 测试证书 ====="
openssl req -x509 -newkey rsa:2048 -keyout /tmp/test_ti.key -out /tmp/test_ti.crt -days 30 -nodes -subj "/CN=ti-server-test" 2>/dev/null
openssl pkcs12 -export -out /tmp/test_ti.pfx -inkey /tmp/test_ti.key -in /tmp/test_ti.crt -passout pass:testpass123 2>/dev/null
ls -la /tmp/test_ti.pfx
echo ""
echo "===== 2. 登录 + 上传 PFX ====="
TOKEN=$(curl -s -X POST "http://127.0.0.1:8090/api/login" -H "Content-Type: application/json" -d '{"user":"admin","pass":"admin"}' --max-time 5 | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))")
PFX_B64=$(base64 -w0 /tmp/test_ti.pfx)
curl -s -X POST "http://127.0.0.1:8090/api/cert" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" \
  -d "{\"action\":\"upload\",\"data\":\"$PFX_B64\",\"pass\":\"testpass123\"}" --max-time 15
echo ""
echo ""
echo "===== 3. 证书状态查询 ====="
curl -s "http://127.0.0.1:8090/api/cert" --max-time 5
echo ""
echo ""
echo "===== 4. 启用 HTTPS ====="
curl -s -X POST "http://127.0.0.1:8090/api/cert" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" \
  -d '{"action":"enable"}' --max-time 5
echo ""
echo ""
echo "===== 5. 重启服务 ====="
systemctl restart ti-server
sleep 3
systemctl is-active ti-server
echo ""
echo "===== 6. HTTPS 访问验证 ====="
curl -sk -o /dev/null -w "https 管理界面: %{http_code}\n" "https://127.0.0.1:8090/" --max-time 5
curl -sk -X POST "https://127.0.0.1:8090/api/login" -H "Content-Type: application/json" -d '{"user":"admin","pass":"admin"}' --max-time 5 | head -c 60
echo ""
echo -n "HTTP 明文访问(应失败): "; curl -s -o /dev/null -w "%{http_code}\n" "http://127.0.0.1:8090/" --max-time 5
echo ""
echo "===== 7. 查询端口不受影响（HTTP） ====="
echo -n "sign: "; curl -s -X POST "http://127.0.0.1:8091/apisix/plugin/jwt/sign?key=wrong" -d "key=wrong" --max-time 5
echo ""
SERVICE_KEY=$(curl -sk "https://127.0.0.1:8090/api/config" -H "Authorization: Bearer $TOKEN" --max-time 5 | python3 -c "import sys,json; print(json.load(sys.stdin)['config']['service_key'])")
JWT=$(curl -s -X POST "http://127.0.0.1:8091/apisix/plugin/jwt/sign?key=$SERVICE_KEY" -d "key=$SERVICE_KEY" --max-time 5)
echo -n "查询命中: "; curl -s "http://127.0.0.1:8091/query?ip=185.220.101.34&jwt=$JWT" --max-time 5 | head -c 100
echo ""
echo ""
echo "===== 8. 流影威胁情报完整闭环（HTTPS 管理 + 查询端口） ====="
COOKIE=/tmp/ly_cookie_https.txt
rm -f $COOKIE
curl -s -X POST "http://127.0.0.1/d/auth" -d "auth_target=login&auth_user=admin&auth_pass=21232f297a57a5a743894a0e4a801fc3" -c $COOKIE --max-time 30 > /dev/null
curl -s -X POST "http://127.0.0.1/d/threatconf" -d "op=save&api_key=&key=$SERVICE_KEY&tic_host=&tic_port=&tisrs_host=127.0.0.1&tisrs_port=8091" -b $COOKIE --max-time 30 > /dev/null
echo -n "threatinfo: "; curl -s "http://127.0.0.1/d/threatinfo?ip=185.220.101.34" -b $COOKIE --max-time 30 | head -c 120
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=400)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1500]}")

client.close()