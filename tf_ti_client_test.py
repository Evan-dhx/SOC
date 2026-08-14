import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("客户端管理全面测试", r"""
echo "===== 1. 登录（HTTPS） ====="
TOKEN=$(curl -sk -X POST "https://127.0.0.1:8090/api/login" -H "Content-Type: application/json" -d '{"user":"admin","pass":"admin"}' --max-time 5 | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))")
echo -n "登录: "; [ -n "$TOKEN" ] && echo OK || echo FAIL
AUTH="Authorization: Bearer $TOKEN"

echo ""
echo "===== 2. 新增客户端（客户A） ====="
curl -sk -X POST "https://127.0.0.1:8090/api/clients" -H "Content-Type: application/json" -H "$AUTH" \
  -d '{"name":"客户A-某某单位","order_no":"TI-2026-001","contact":"张三 138xxxx","allowed_ips":"127.0.0.1","update_window":"00:00-23:59"}' --max-time 5
echo ""

echo ""
echo "===== 3. 客户端列表 ====="
curl -sk "https://127.0.0.1:8090/api/clients" -H "$AUTH" --max-time 5 | python3 -c "
import sys, json
d = json.load(sys.stdin)
for c in d['data']:
    print(f\"id={c['id']} name={c['name']} order={c['order_no']} enabled={c['enabled']} ips={c['allowed_ips']} win={c['update_window']}\")
    print(f\"   key={c['cli_key']}\")
    print(f\"   token={c['cli_token']}\")
"
CLIENT_KEY=$(curl -sk "https://127.0.0.1:8090/api/clients" -H "$AUTH" --max-time 5 | python3 -c "import sys,json; d=json.load(sys.stdin); print([c['cli_key'] for c in d['data'] if c['name'].startswith('客户A')][0])")
CLIENT_TOKEN=$(curl -sk "https://127.0.0.1:8090/api/clients" -H "$AUTH" --max-time 5 | python3 -c "import sys,json; d=json.load(sys.stdin); print([c['cli_token'] for c in d['data'] if c['name'].startswith('客户A')][0])")
CLIENT_ID=$(curl -sk "https://127.0.0.1:8090/api/clients" -H "$AUTH" --max-time 5 | python3 -c "import sys,json; d=json.load(sys.stdin); print([c['id'] for c in d['data'] if c['name'].startswith('客户A')][0])")

echo ""
echo "===== 4. 客户端 key 换 JWT（来源 127.0.0.1 在允许列表） ====="
JWT=$(curl -s -X POST "http://127.0.0.1:8091/apisix/plugin/jwt/sign?key=$CLIENT_KEY" -d "key=$CLIENT_KEY" --max-time 5)
echo -n "JWT: ${JWT:0:30}...  "
echo -n "查询命中: "; curl -s "http://127.0.0.1:8091/query?ip=185.220.101.34&jwt=$JWT" --max-time 5 | head -c 80
echo ""

echo ""
echo "===== 5. 禁用客户端 → key 被拒 ====="
curl -sk -X PUT "https://127.0.0.1:8090/api/clients/$CLIENT_ID" -H "Content-Type: application/json" -H "$AUTH" \
  -d '{"name":"客户A-某某单位","order_no":"TI-2026-001","contact":"张三","allowed_ips":"127.0.0.1","update_window":"00:00-23:59","enabled":0}' --max-time 5 > /dev/null
echo -n "禁用后 sign: "; curl -s -X POST "http://127.0.0.1:8091/apisix/plugin/jwt/sign?key=$CLIENT_KEY" -d "key=$CLIENT_KEY" --max-time 5
echo ""
echo -n "禁用后 token 直查: "; curl -s "http://127.0.0.1:8091/query?ip=185.220.101.34&token=$CLIENT_TOKEN" --max-time 5
echo ""

echo ""
echo "===== 6. 重新启用 + IP 白名单拒绝 ====="
curl -sk -X PUT "https://127.0.0.1:8090/api/clients/$CLIENT_ID" -H "Content-Type: application/json" -H "$AUTH" \
  -d '{"name":"客户A-某某单位","order_no":"TI-2026-001","contact":"张三","allowed_ips":"10.0.0.0/8","update_window":"00:00-23:59","enabled":1}' --max-time 5 > /dev/null
echo -n "IP不在白名单(127.0.0.1): "; curl -s -X POST "http://127.0.0.1:8091/apisix/plugin/jwt/sign?key=$CLIENT_KEY" -d "key=$CLIENT_KEY" --max-time 5
echo ""
curl -sk -X PUT "https://127.0.0.1:8090/api/clients/$CLIENT_ID" -H "Content-Type: application/json" -H "$AUTH" \
  -d '{"name":"客户A-某某单位","order_no":"TI-2026-001","contact":"张三","allowed_ips":"127.0.0.1","update_window":"00:00-23:59","enabled":1}' --max-time 5 > /dev/null
echo -n "恢复后 sign: "; curl -s -X POST "http://127.0.0.1:8091/apisix/plugin/jwt/sign?key=$CLIENT_KEY" -d "key=$CLIENT_KEY" --max-time 5 | head -c 40
echo ""

echo ""
echo "===== 7. token 直查 + export 全量更新 ====="
echo -n "token直查: "; curl -s "http://127.0.0.1:8091/query?ip=185.220.101.34&token=$CLIENT_TOKEN" --max-time 5 | head -c 80
echo ""
echo -n "export: "; curl -s "http://127.0.0.1:8091/export?token=$CLIENT_TOKEN" --max-time 5 | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"code={d['code']} total={d.get('total')}\")"
echo -n "更新记录: "; curl -sk "https://127.0.0.1:8090/api/clients/$CLIENT_ID/log" -H "$AUTH" --max-time 5 | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"last={d['last_update']} log={d['log'][:60]}\")"
echo ""

echo ""
echo "===== 8. 时间窗口限制 ====="
NOW=$(date +%H:%M)
echo "当前时间: $NOW"
curl -sk -X PUT "https://127.0.0.1:8090/api/clients/$CLIENT_ID" -H "Content-Type: application/json" -H "$AUTH" \
  -d '{"name":"客户A-某某单位","order_no":"TI-2026-001","contact":"张三","allowed_ips":"127.0.0.1","update_window":"23:58-23:59","enabled":1}' --max-time 5 > /dev/null
echo -n "窗口外 export: "; curl -s "http://127.0.0.1:8091/export?token=$CLIENT_TOKEN" --max-time 5
echo ""
curl -sk -X PUT "https://127.0.0.1:8090/api/clients/$CLIENT_ID" -H "Content-Type: application/json" -H "$AUTH" \
  -d '{"name":"客户A-某某单位","order_no":"TI-2026-001","contact":"张三","allowed_ips":"127.0.0.1","update_window":"00:00-23:59","enabled":1}' --max-time 5 > /dev/null

echo ""
echo "===== 9. 重置 Key/Token ====="
curl -sk -X POST "https://127.0.0.1:8090/api/clients/$CLIENT_ID/regen" -H "Content-Type: application/json" -H "$AUTH" -d '{"kind":"key"}' --max-time 5 | head -c 120
echo ""
echo -n "旧key已失效: "; curl -s -X POST "http://127.0.0.1:8091/apisix/plugin/jwt/sign?key=$CLIENT_KEY" -d "key=$CLIENT_KEY" --max-time 5
echo ""
echo ""

echo "===== 10. 流影对接（用客户A的 key） ====="
COOKIE=/tmp/ly_cookie_client.txt
rm -f $COOKIE
curl -s -X POST "http://127.0.0.1/d/auth" -d "auth_target=login&auth_user=admin&auth_pass=21232f297a57a5a743894a0e4a801fc3" -c $COOKIE --max-time 30 > /dev/null
NEW_KEY=$(curl -sk "https://127.0.0.1:8090/api/clients" -H "$AUTH" --max-time 5 | python3 -c "import sys,json; d=json.load(sys.stdin); print([c['cli_key'] for c in d['data'] if c['name'].startswith('客户A')][0])")
curl -s -X POST "http://127.0.0.1/d/threatconf" -d "op=save&api_key=&key=$NEW_KEY&tic_host=&tic_port=&tisrs_host=127.0.0.1&tisrs_port=8091" -b $COOKIE --max-time 30
echo ""
echo -n "threatinfo(客户A key): "; curl -s "http://127.0.0.1/d/threatinfo?ip=185.220.101.34" -b $COOKIE --max-time 30 | head -c 90
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