import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("ti_server 全面测试", r"""
echo "===== 1. 管理界面 ====="
curl -s -o /dev/null -w "GET /: %{http_code}\n" "http://127.0.0.1:8090/" --max-time 5
curl -s -o /dev/null -w "静态文件: %{http_code}\n" "http://127.0.0.1:8090/static/index.html" --max-time 5

echo ""
echo "===== 2. 登录 ====="
TOKEN=$(curl -s -X POST "http://127.0.0.1:8090/api/login" -H "Content-Type: application/json" -d '{"user":"admin","pass":"admin"}' --max-time 5 | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))")
echo "token: ${TOKEN:0:16}..."
echo -n "错误密码: "; curl -s -X POST "http://127.0.0.1:8090/api/login" -H "Content-Type: application/json" -d '{"user":"admin","pass":"wrong"}' --max-time 5
echo ""
echo -n "无token访问stats: "; curl -s "http://127.0.0.1:8090/api/stats" --max-time 5
echo ""

echo ""
echo "===== 3. 新增情报（4 类型） ====="
for body in '{"type":"ip","value":"185.220.101.34","threat":"botnet","score":95,"tags":"僵尸网络,C2","source":"内部测试"}' '{"type":"domain","value":"evil-c2.example.com","threat":"dga","score":85,"tags":"DGA","source":"内部测试"}' '{"type":"url","value":"http://malware.example.com/payload","threat":"trojan","score":90,"tags":"恶意下载","source":"内部测试"}' '{"type":"hash","value":"5d41402abc4b2a76b9719d911017c592","threat":"malware","score":75,"tags":"恶意样本","source":"内部测试"}'; do
  curl -s -X POST "http://127.0.0.1:8090/api/iocs" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d "$body" --max-time 5
  echo ""
done

echo ""
echo "===== 4. 批量导入 ====="
curl -s -X POST "http://127.0.0.1:8090/api/iocs/batch" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d '{"items":[{"type":"ip","value":"45.155.205.233","threat":"scan","score":70,"source":"开源情报"},{"type":"domain","value":"phishing.example.net","threat":"phishing","score":88,"tags":"钓鱼"},{"type":"ip","value":"185.220.101.34","threat":"botnet","score":99,"source":"重复测试"}]}' --max-time 5
echo ""

echo ""
echo "===== 5. 列表与筛选 ====="
echo -n "全部: "; curl -s "http://127.0.0.1:8090/api/iocs?page=1&size=20" -H "Authorization: Bearer $TOKEN" --max-time 5 | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"total={d['total']}\")"
echo -n "类型=ip: "; curl -s "http://127.0.0.1:8090/api/iocs?type=ip" -H "Authorization: Bearer $TOKEN" --max-time 5 | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"total={d['total']}, 第一条={d['data'][0]['value'] if d['data'] else ''}\")"
echo -n "搜索=evil: "; curl -s "http://127.0.0.1:8090/api/iocs?q=evil" -H "Authorization: Bearer $TOKEN" --max-time 5 | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"total={d['total']}\")"
echo -n "统计: "; curl -s "http://127.0.0.1:8090/api/stats" -H "Authorization: Bearer $TOKEN" --max-time 5

echo ""
echo ""
echo "===== 6. 修改与删除 ====="
ID=$(curl -s "http://127.0.0.1:8090/api/iocs?type=hash" -H "Authorization: Bearer $TOKEN" --max-time 5 | python3 -c "import sys,json; print(json.load(sys.stdin)['data'][0]['id'])")
echo -n "修改 #$ID: "; curl -s -X PUT "http://127.0.0.1:8090/api/iocs/$ID" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d '{"type":"hash","value":"5d41402abc4b2a76b9719d911017c592","threat":"ransomware","score":80,"source":"更新"}' --max-time 5
echo ""
echo -n "删除 #$ID: "; curl -s -X DELETE "http://127.0.0.1:8090/api/iocs/$ID" -H "Authorization: Bearer $TOKEN" --max-time 5
echo ""

echo ""
echo "===== 7. 配置读取 ====="
curl -s "http://127.0.0.1:8090/api/config" -H "Authorization: Bearer $TOKEN" --max-time 5
echo ""
SERVICE_KEY=$(curl -s "http://127.0.0.1:8090/api/config" -H "Authorization: Bearer $TOKEN" --max-time 5 | python3 -c "import sys,json; print(json.load(sys.stdin)['config']['service_key'])")
echo "service_key: ${SERVICE_KEY:0:12}..."

echo ""
echo "===== 8. JWT 签发 ====="
echo -n "正确key: "; curl -s -X POST "http://127.0.0.1:8090/apisix/plugin/jwt/sign?key=$SERVICE_KEY" -d "key=$SERVICE_KEY" --max-time 5
echo ""
echo -n "错误key: "; curl -s -X POST "http://127.0.0.1:8090/apisix/plugin/jwt/sign?key=wrong" -d "key=wrong" --max-time 5
echo ""

echo ""
echo "===== 9. 情报查询 ====="
JWT=$(curl -s -X POST "http://127.0.0.1:8090/apisix/plugin/jwt/sign?key=$SERVICE_KEY" -d "key=$SERVICE_KEY" --max-time 5 | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))")
echo -n "命中IP: "; curl -s "http://127.0.0.1:8090/query?ip=185.220.101.34&jwt=$JWT" --max-time 5
echo ""
echo -n "命中域名: "; curl -s "http://127.0.0.1:8090/query?domain=evil-c2.example.com&jwt=$JWT" --max-time 5
echo ""
echo -n "未命中: "; curl -s "http://127.0.0.1:8090/query?ip=8.8.8.8&jwt=$JWT" --max-time 5
echo ""
echo -n "无JWT: "; curl -s "http://127.0.0.1:8090/query?ip=185.220.101.34" --max-time 5
echo ""
echo -n "根路径查询: "; curl -s "http://127.0.0.1:8090/?ip=45.155.205.233&jwt=$JWT" --max-time 5
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