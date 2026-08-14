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
    ("重启服务 + 回归测试", r"""
echo "=== 1. 重启 ==="
systemctl restart ti-server
sleep 2
systemctl is-active ti-server
echo ""
echo "=== 2. 管理界面 ==="
curl -s -o /dev/null -w "GET /: %{http_code}\n" "http://127.0.0.1:8090/" --max-time 5
curl -s "http://127.0.0.1:8090/" --max-time 5 | grep -o "天鯨" | head -1
echo ""
echo "=== 3. 登录 + 查询全链路 ==="
TOKEN=$(curl -s -X POST "http://127.0.0.1:8090/api/login" -H "Content-Type: application/json" -d '{"user":"admin","pass":"admin"}' --max-time 5 | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))")
SERVICE_KEY=$(curl -s "http://127.0.0.1:8090/api/config" -H "Authorization: Bearer $TOKEN" --max-time 5 | python3 -c "import sys,json; print(json.load(sys.stdin)['config']['service_key'])")
JWT=$(curl -s -X POST "http://127.0.0.1:8090/apisix/plugin/jwt/sign?key=$SERVICE_KEY" -d "key=$SERVICE_KEY" --max-time 5 | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))")
echo -n "命中IP: "; curl -s "http://127.0.0.1:8090/query?ip=185.220.101.34&jwt=$JWT" --max-time 5
echo ""
echo -n "命中域名: "; curl -s "http://127.0.0.1:8090/query?domain=evil-c2.example.com&jwt=$JWT" --max-time 5
echo ""
echo -n "未命中: "; curl -s "http://127.0.0.1:8090/query?ip=8.8.8.8&jwt=$JWT" --max-time 5
echo ""
echo -n "无JWT: "; curl -s "http://127.0.0.1:8090/query?ip=185.220.101.34" --max-time 5
echo ""
echo -n "POST查询: "; curl -s -X POST "http://127.0.0.1:8090/query?domain=phishing.example.net&jwt=$JWT" --max-time 5
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