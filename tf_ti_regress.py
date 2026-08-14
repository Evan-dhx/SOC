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
    ("重启 + 完整回归", r"""
echo "=== 1. 重启 ==="
systemctl restart ti-server
sleep 2
systemctl is-active ti-server
echo ""
echo "=== 2. 管理界面访问 ==="
curl -s -o /dev/null -w "GET /: %{http_code}\n" "http://127.0.0.1:8090/" --max-time 5
curl -s "http://127.0.0.1:8090/" --max-time 5 | grep -o "天鯨" | head -1
echo ""
echo "=== 3. 认证隔离 ==="
echo -n "无token stats: "; curl -s "http://127.0.0.1:8090/api/stats" --max-time 5
echo ""
echo -n "无token iocs: "; curl -s "http://127.0.0.1:8090/api/iocs" --max-time 5
echo ""
echo "=== 4. 查询全链路（管理界面修复不影响查询） ==="
TOKEN=$(curl -s -X POST "http://127.0.0.1:8090/api/login" -H "Content-Type: application/json" -d '{"user":"admin","pass":"admin"}' --max-time 5 | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))")
SERVICE_KEY=$(curl -s "http://127.0.0.1:8090/api/config" -H "Authorization: Bearer $TOKEN" --max-time 5 | python3 -c "import sys,json; print(json.load(sys.stdin)['config']['service_key'])")
JWT=$(curl -s -X POST "http://127.0.0.1:8090/apisix/plugin/jwt/sign?key=$SERVICE_KEY" -d "key=$SERVICE_KEY" --max-time 5 | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))")
echo -n "命中IP: "; curl -s "http://127.0.0.1:8090/query?ip=185.220.101.34&jwt=$JWT" --max-time 5 | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"{len(d)}条, threat={d[0]['threat']}\")"
echo -n "统计: "; curl -s "http://127.0.0.1:8090/api/stats" -H "Authorization: Bearer $TOKEN" --max-time 5
echo ""
echo -n "改密码(错误旧密码): "; curl -s -X POST "http://127.0.0.1:8090/api/password" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d '{"old":"wrong","new":"newpass"}' --max-time 5
echo ""
echo -n "改密码(正确): "; curl -s -X POST "http://127.0.0.1:8090/api/password" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d '{"old":"admin","new":"admin"}' --max-time 5
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