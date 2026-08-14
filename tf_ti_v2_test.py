import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("v2 全面测试", r"""
echo "===== 1. 双端口状态 ====="
ss -tlnp 2>/dev/null | grep -E "8090|8091" | awk '{print $4}'
echo ""
echo "===== 2. 管理端口（8090） ====="
curl -s -o /dev/null -w "GET /: %{http_code}\n" "http://127.0.0.1:8090/" --max-time 5
TOKEN=$(curl -s -X POST "http://127.0.0.1:8090/api/login" -H "Content-Type: application/json" -d '{"user":"admin","pass":"admin"}' --max-time 5 | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))")
echo -n "登录: "; [ -n "$TOKEN" ] && echo "OK" || echo "FAIL"
echo -n "管理端口调查询协议: "; curl -s "http://127.0.0.1:8090/query?ip=1.2.3.4" --max-time 5
echo ""
echo ""
echo "===== 3. 查询端口（8091） ====="
echo -n "无jwt: "; curl -s "http://127.0.0.1:8091/query?ip=1.2.3.4" --max-time 5
echo ""
echo -n "调管理API(应404): "; curl -s "http://127.0.0.1:8091/api/stats" --max-time 5
echo ""
echo -n "管理界面(应404): "; curl -s -o /dev/null -w "%{http_code}\n" "http://127.0.0.1:8091/" --max-time 5
echo ""
echo "===== 4. 灌入示例情报（MySQL） ====="
for body in '{"type":"ip","value":"185.220.101.34","threat":"botnet","score":95,"tags":"僵尸网络,C2","source":"MySQL迁移测试"}' '{"type":"domain","value":"evil-c2.example.com","threat":"dga","score":85,"tags":"DGA","source":"MySQL迁移测试"}' '{"type":"ip","value":"45.155.205.233","threat":"scan","score":70,"source":"MySQL迁移测试"}'; do
  curl -s -X POST "http://127.0.0.1:8090/api/iocs" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d "$body" --max-time 5 > /dev/null
done
echo "已添加 3 条"
echo -n "MySQL 实际数据: "; mysql -uroot -ppassword123 ti_server -e "SELECT id,type,value,threat,score FROM t_ioc;" 2>/dev/null
echo ""
echo "===== 5. 查询闭环（8091） ====="
SERVICE_KEY=$(curl -s "http://127.0.0.1:8090/api/config" -H "Authorization: Bearer $TOKEN" --max-time 5 | python3 -c "import sys,json; print(json.load(sys.stdin)['config']['service_key'])")
JWT=$(curl -s -X POST "http://127.0.0.1:8091/apisix/plugin/jwt/sign?key=$SERVICE_KEY" -d "key=$SERVICE_KEY" --max-time 5)
echo -n "命中IP: "; curl -s "http://127.0.0.1:8091/query?ip=185.220.101.34&jwt=$JWT" --max-time 5 | head -c 180
echo ""
echo -n "未命中: "; curl -s "http://127.0.0.1:8091/query?ip=8.8.8.8&jwt=$JWT" --max-time 5
echo ""
echo ""
echo "===== 6. 流影对接（指向查询端口 8091） ====="
COOKIE=/tmp/ly_cookie_v2.txt
rm -f $COOKIE
curl -s -X POST "http://127.0.0.1/d/auth" -d "auth_target=login&auth_user=admin&auth_pass=21232f297a57a5a743894a0e4a801fc3" -c $COOKIE --max-time 30 > /dev/null
curl -s -X POST "http://127.0.0.1/d/threatconf" -d "op=save&api_key=&key=$SERVICE_KEY&tic_host=&tic_port=&tisrs_host=127.0.0.1&tisrs_port=8091" -b $COOKIE --max-time 30
echo ""
echo -n "threatinfo 命中: "; curl -s "http://127.0.0.1/d/threatinfo?ip=185.220.101.34" -b $COOKIE --max-time 30 | head -c 160
echo ""
echo -n "threatinfo 未命中: "; curl -s "http://127.0.0.1/d/threatinfo?ip=8.8.8.8" -b $COOKIE --max-time 30
echo ""
echo -n "测试按钮: "; curl -s -X POST "http://127.0.0.1/d/threatconf" -d "op=test" -b $COOKIE --max-time 30
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