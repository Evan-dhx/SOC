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
    ("重启 + 安全功能重测", r"""
systemctl restart ti-server
sleep 3
systemctl is-active ti-server
echo ""
echo "===== 1. 登录 + 取客户A信息 ====="
TOKEN=$(curl -sk -X POST "https://127.0.0.1:8090/api/login" -H "Content-Type: application/json" -d '{"user":"admin","pass":"admin"}' --max-time 5 | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))")
AUTH="Authorization: Bearer $TOKEN"
CLIENT_ID=$(curl -sk "https://127.0.0.1:8090/api/clients" -H "$AUTH" --max-time 5 | python3 -c "import sys,json; d=json.load(sys.stdin); print([c['id'] for c in d['data'] if c['name'].startswith('客户A')][0])")
CLIENT_KEY=$(curl -sk "https://127.0.0.1:8090/api/clients" -H "$AUTH" --max-time 5 | python3 -c "import sys,json; d=json.load(sys.stdin); print([c['cli_key'] for c in d['data'] if c['name'].startswith('客户A')][0])")
CLIENT_TOKEN=$(curl -sk "https://127.0.0.1:8090/api/clients" -H "$AUTH" --max-time 5 | python3 -c "import sys,json; d=json.load(sys.stdin); print([c['cli_token'] for c in d['data'] if c['name'].startswith('客户A')][0])")
echo "客户A id=$CLIENT_ID"

echo ""
echo "===== 2. 禁用 → sign 应被拒 ====="
curl -sk -X PUT "https://127.0.0.1:8090/api/clients/$CLIENT_ID" -H "Content-Type: application/json" -H "$AUTH" \
  -d '{"name":"客户A-某某单位","order_no":"TI-2026-001","contact":"张三","allowed_ips":"127.0.0.1","update_window":"00:00-23:59","enabled":0}' --max-time 5
echo ""
echo -n "sign(禁用): "; curl -s -X POST "http://127.0.0.1:8091/apisix/plugin/jwt/sign?key=$CLIENT_KEY" -d "key=$CLIENT_KEY" --max-time 5
echo ""
echo -n "token直查(禁用): "; curl -s "http://127.0.0.1:8091/query?ip=185.220.101.34&token=$CLIENT_TOKEN" --max-time 5
echo ""

echo ""
echo "===== 3. 启用 + IP 白名单拒绝 ====="
curl -sk -X PUT "https://127.0.0.1:8090/api/clients/$CLIENT_ID" -H "Content-Type: application/json" -H "$AUTH" \
  -d '{"name":"客户A-某某单位","order_no":"TI-2026-001","contact":"张三","allowed_ips":"10.0.0.0/8","update_window":"00:00-23:59","enabled":1}' --max-time 5 > /dev/null
echo -n "sign(IP不在白名单): "; curl -s -X POST "http://127.0.0.1:8091/apisix/plugin/jwt/sign?key=$CLIENT_KEY" -d "key=$CLIENT_KEY" --max-time 5
echo ""
curl -sk -X PUT "https://127.0.0.1:8090/api/clients/$CLIENT_ID" -H "Content-Type: application/json" -H "$AUTH" \
  -d '{"name":"客户A-某某单位","order_no":"TI-2026-001","contact":"张三","allowed_ips":"127.0.0.1","update_window":"00:00-23:59","enabled":1}' --max-time 5 > /dev/null
echo -n "恢复后 sign: "; curl -s -X POST "http://127.0.0.1:8091/apisix/plugin/jwt/sign?key=$CLIENT_KEY" -d "key=$CLIENT_KEY" --max-time 5 | head -c 30
echo ""

echo ""
echo "===== 4. 时间窗口限制（当前 $(date +%H:%M)，设 23:58-23:59） ====="
curl -sk -X PUT "https://127.0.0.1:8090/api/clients/$CLIENT_ID" -H "Content-Type: application/json" -H "$AUTH" \
  -d '{"name":"客户A-某某单位","order_no":"TI-2026-001","contact":"张三","allowed_ips":"127.0.0.1","update_window":"23:58-23:59","enabled":1}' --max-time 5 > /dev/null
echo -n "export(窗口外): "; curl -s "http://127.0.0.1:8091/export?token=$CLIENT_TOKEN" --max-time 5
echo ""
curl -sk -X PUT "https://127.0.0.1:8090/api/clients/$CLIENT_ID" -H "Content-Type: application/json" -H "$AUTH" \
  -d '{"name":"客户A-某某单位","order_no":"TI-2026-001","contact":"张三","allowed_ips":"127.0.0.1","update_window":"00:00-23:59","enabled":1}' --max-time 5 > /dev/null
echo -n "恢复窗口后 export: "; curl -s "http://127.0.0.1:8091/export?token=$CLIENT_TOKEN" --max-time 5 | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"code={d['code']} total={d.get('total')}\")"

echo ""
echo "===== 5. 更新记录（应累计 2 条） ====="
curl -sk "https://127.0.0.1:8090/api/clients/$CLIENT_ID/log" -H "$AUTH" --max-time 5 | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['log'])"
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