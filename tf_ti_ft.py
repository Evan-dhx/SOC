import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("① 基础服务与认证", r"""
P(){ echo -n "$1: "; shift; "$@" --max-time 6 2>/dev/null; echo ""; }
echo "===== A1. 服务与端口 ====="
echo -n "systemd: "; systemctl is-active ti-server
echo -n "8090/8091: "; ss -tlnp 2>/dev/null | grep -cE "8090|8091"
echo ""
echo "===== A2. 管理登录认证（HTTPS 8090） ====="
P "正确密码"      curl -sk -X POST "https://127.0.0.1:8090/api/login" -H "Content-Type: application/json" -d '{"user":"admin","pass":"admin"}'
P "错误密码"      curl -sk -X POST "https://127.0.0.1:8090/api/login" -H "Content-Type: application/json" -d '{"user":"admin","pass":"wrong"}'
P "不存在用户"    curl -sk -X POST "https://127.0.0.1:8090/api/login" -H "Content-Type: application/json" -d '{"user":"nobody","pass":"x"}'
P "无token访问API" curl -sk "https://127.0.0.1:8090/api/stats"
P "HTTP明文被拒"   curl -s "http://127.0.0.1:8090/" -o /dev/null -w "%{http_code}"
P "HTTP明文API"    curl -s "http://127.0.0.1:8090/api/stats"
echo ""
echo "===== A3. 查询端口认证（HTTP 8091） ====="
P "无凭据查询"    curl -s "http://127.0.0.1:8091/query?ip=1.2.3.4"
P "错误key签发"   curl -s -X POST "http://127.0.0.1:8091/apisix/plugin/jwt/sign?key=wrong_key" -d "key=wrong_key"
P "错误token查询" curl -s "http://127.0.0.1:8091/query?ip=1.2.3.4&token=wrong_token"
P "伪造JWT查询"   curl -s "http://127.0.0.1:8091/query?ip=1.2.3.4&jwt=abc.def.ghi"
P "管理API隔离"   curl -s "http://127.0.0.1:8091/api/stats"
"""),
    ("② 客户端管理功能", r"""
TOKEN=$(curl -sk -X POST "https://127.0.0.1:8090/api/login" -H "Content-Type: application/json" -d '{"user":"admin","pass":"admin"}' --max-time 6 | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))")
AUTH="Authorization: Bearer $TOKEN"
P(){ echo -n "$1: "; shift; "$@" --max-time 6 2>/dev/null; echo ""; }
echo "===== B1. 字段校验 ====="
P "空名称"        curl -sk -X POST "https://127.0.0.1:8090/api/clients" -H "Content-Type: application/json" -H "$AUTH" -d '{"name":""}'
P "非法IP"        curl -sk -X POST "https://127.0.0.1:8090/api/clients" -H "Content-Type: application/json" -H "$AUTH" -d '{"name":"测试","allowed_ips":"999.1.1.1"}'
P "非法窗口"      curl -sk -X POST "https://127.0.0.1:8090/api/clients" -H "Content-Type: application/json" -H "$AUTH" -d '{"name":"测试","update_window":"25:99-26:00"}'
echo ""
echo "===== B2. 新增两个测试客户端 ====="
P "新增客户X"     curl -sk -X POST "https://127.0.0.1:8090/api/clients" -H "Content-Type: application/json" -H "$AUTH" -d '{"name":"功能测试-客户X","order_no":"TEST-001","contact":"测试","allowed_ips":"127.0.0.1","update_window":"00:00-23:59","enabled":1}'
P "新增客户Y(禁用)" curl -sk -X POST "https://127.0.0.1:8090/api/clients" -H "Content-Type: application/json" -H "$AUTH" -d '{"name":"功能测试-客户Y","order_no":"TEST-002","enabled":0}'
CID_X=$(curl -sk "https://127.0.0.1:8090/api/clients" -H "$AUTH" --max-time 6 | python3 -c "import sys,json; d=json.load(sys.stdin); print([c['id'] for c in d['data'] if c['name']=='功能测试-客户X'][0])")
CID_Y=$(curl -sk "https://127.0.0.1:8090/api/clients" -H "$AUTH" --max-time 6 | python3 -c "import sys,json; d=json.load(sys.stdin); print([c['id'] for c in d['data'] if c['name']=='功能测试-客户Y'][0])")
echo "客户X id=$CID_X, 客户Y id=$CID_Y"
echo ""
echo "===== B3. 编辑/启用禁用 ====="
P "编辑客户X"     curl -sk -X PUT "https://127.0.0.1:8090/api/clients/$CID_X" -H "Content-Type: application/json" -H "$AUTH" -d '{"name":"功能测试-客户X改","order_no":"TEST-001A","allowed_ips":"127.0.0.1,10.0.0.0/8","update_window":"00:00-23:59","enabled":1}'
P "编辑不存在的"  curl -sk -X PUT "https://127.0.0.1:8090/api/clients/9999" -H "Content-Type: application/json" -H "$AUTH" -d '{"name":"x","enabled":1}'
P "启用客户Y"     curl -sk -X PUT "https://127.0.0.1:8090/api/clients/$CID_Y" -H "Content-Type: application/json" -H "$AUTH" -d '{"name":"功能测试-客户Y","order_no":"TEST-002","enabled":1}'
echo ""
echo "===== B4. Key/Token 重置 ====="
P "重置X的Key"    curl -sk -X POST "https://127.0.0.1:8090/api/clients/$CID_X/regen" -H "Content-Type: application/json" -H "$AUTH" -d '{"kind":"key"}'
P "非法kind"      curl -sk -X POST "https://127.0.0.1:8090/api/clients/$CID_X/regen" -H "Content-Type: application/json" -H "$AUTH" -d '{"kind":"other"}'
echo ""
echo "===== B5. 删除 ====="
P "删除客户Y"     curl -sk -X DELETE "https://127.0.0.1:8090/api/clients/$CID_Y" -H "$AUTH"
P "重复删除"      curl -sk -X DELETE "https://127.0.0.1:8090/api/clients/$CID_Y" -H "$AUTH"
echo ""
echo "===== B6. 更新记录接口 ====="
P "客户X记录"     curl -sk "https://127.0.0.1:8090/api/clients/$CID_X/log" -H "$AUTH"
P "不存在记录"    curl -sk "https://127.0.0.1:8090/api/clients/9999/log" -H "$AUTH"
"""),
    ("③ 情报管理功能", r"""
TOKEN=$(curl -sk -X POST "https://127.0.0.1:8090/api/login" -H "Content-Type: application/json" -d '{"user":"admin","pass":"admin"}' --max-time 6 | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))")
AUTH="Authorization: Bearer $TOKEN"
P(){ echo -n "$1: "; shift; "$@" --max-time 6 2>/dev/null; echo ""; }
echo "===== C1. 新增 4 类型情报 ====="
P "IP"    curl -sk -X POST "https://127.0.0.1:8090/api/iocs" -H "Content-Type: application/json" -H "$AUTH" -d '{"type":"ip","value":"198.51.100.7","threat":"c2","score":92,"tags":"测试,C2"}'
P "域名"  curl -sk -X POST "https://127.0.0.1:8090/api/iocs" -H "Content-Type: application/json" -H "$AUTH" -d '{"type":"domain","value":"test-c2.example.org","threat":"dga","score":80}'
P "URL"   curl -sk -X POST "https://127.0.0.1:8090/api/iocs" -H "Content-Type: application/json" -H "$AUTH" -d '{"type":"url","value":"http://bad.example.org/x","threat":"malware","score":88}'
P "哈希"  curl -sk -X POST "https://127.0.0.1:8090/api/iocs" -H "Content-Type: application/json" -H "$AUTH" -d '{"type":"hash","value":"e8dc4081b13434b45189a72022777a64","threat":"malware","score":77}'
P "非法类型" curl -sk -X POST "https://127.0.0.1:8090/api/iocs" -H "Content-Type: application/json" -H "$AUTH" -d '{"type":"email","value":"a@b.com"}'
P "空值"     curl -sk -X POST "https://127.0.0.1:8090/api/iocs" -H "Content-Type: application/json" -H "$AUTH" -d '{"type":"ip","value":""}'
echo ""
echo "===== C2. 筛选与分页 ====="
P "类型=domain"  curl -sk "https://127.0.0.1:8090/api/iocs?type=domain" -H "$AUTH"
P "威胁=c2"      curl -sk "https://127.0.0.1:8090/api/iocs?threat=c2" -H "$AUTH"
P "关键字=test"  curl -sk "https://127.0.0.1:8090/api/iocs?q=test" -H "$AUTH"
P "分页size=2"   curl -sk "https://127.0.0.1:8090/api/iocs?page=1&size=2" -H "$AUTH"
echo ""
echo "===== C3. 批量导入 ====="
P "导入3条"      curl -sk -X POST "https://127.0.0.1:8090/api/iocs/batch" -H "Content-Type: application/json" -H "$AUTH" -d '{"items":[{"type":"ip","value":"198.51.100.8","threat":"scan"},{"type":"ip","value":"198.51.100.9","threat":"scan"},{"type":"bad","value":"x"}]}'
P "空导入"       curl -sk -X POST "https://127.0.0.1:8090/api/iocs/batch" -H "Content-Type: application/json" -H "$AUTH" -d '{"items":[]}'
echo ""
echo "===== C4. 修改与删除 ====="
NID=$(curl -sk "https://127.0.0.1:8090/api/iocs?q=test-c2" -H "$AUTH" --max-time 6 | python3 -c "import sys,json; print(json.load(sys.stdin)['data'][0]['id'])")
P "修改 #$NID"   curl -sk -X PUT "https://127.0.0.1:8090/api/iocs/$NID" -H "Content-Type: application/json" -H "$AUTH" -d '{"type":"domain","value":"test-c2.example.org","threat":"ransomware","score":90}'
P "删除 #$NID"   curl -sk -X DELETE "https://127.0.0.1:8090/api/iocs/$NID" -H "$AUTH"
P "删除不存在"   curl -sk -X DELETE "https://127.0.0.1:8090/api/iocs/99999" -H "$AUTH"
echo ""
echo "===== C5. 统计 ====="
P "stats"        curl -sk "https://127.0.0.1:8090/api/stats" -H "$AUTH"
"""),
    ("④ 查询协议与安全策略", r"""
TOKEN=$(curl -sk -X POST "https://127.0.0.1:8090/api/login" -H "Content-Type: application/json" -d '{"user":"admin","pass":"admin"}' --max-time 6 | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))")
AUTH="Authorization: Bearer $TOKEN"
CID_X=$(curl -sk "https://127.0.0.1:8090/api/clients" -H "$AUTH" --max-time 6 | python3 -c "import sys,json; d=json.load(sys.stdin); print([c['id'] for c in d['data'] if c['name']=='功能测试-客户X改'][0])")
KEY_X=$(curl -sk "https://127.0.0.1:8090/api/clients" -H "$AUTH" --max-time 6 | python3 -c "import sys,json; d=json.load(sys.stdin); print([c['cli_key'] for c in d['data'] if c['name']=='功能测试-客户X改'][0])")
TOK_X=$(curl -sk "https://127.0.0.1:8090/api/clients" -H "$AUTH" --max-time 6 | python3 -c "import sys,json; d=json.load(sys.stdin); print([c['cli_token'] for c in d['data'] if c['name']=='功能测试-客户X改'][0])")
P(){ echo -n "$1: "; shift; "$@" --max-time 6 2>/dev/null; echo ""; }
echo "===== D1. JWT 签发（客户端 key） ====="
JWT=$(curl -s -X POST "http://127.0.0.1:8091/apisix/plugin/jwt/sign?key=$KEY_X" -d "key=$KEY_X" --max-time 6)
echo -n "签发: "; [ -n "$JWT" ] && echo "OK (${JWT:0:25}...)" || echo "FAIL"
echo ""
echo "===== D2. 情报查询（jwt） ====="
P "命中IP(198.51.100.7)" curl -s "http://127.0.0.1:8091/query?ip=198.51.100.7&jwt=$JWT"
P "命中URL"              curl -s "http://127.0.0.1:8091/query?url=http://bad.example.org/x&jwt=$JWT"
P "命中哈希"             curl -s "http://127.0.0.1:8091/query?hash=e8dc4081b13434b45189a72022777a64&jwt=$JWT"
P "未命中"               curl -s "http://127.0.0.1:8091/query?ip=203.0.113.99&jwt=$JWT"
echo ""
echo "===== D3. token 直查 ====="
P "token命中"  curl -s "http://127.0.0.1:8091/query?ip=198.51.100.7&token=$TOK_X"
echo ""
echo "===== D4. IP 白名单 ====="
curl -sk -X PUT "https://127.0.0.1:8090/api/clients/$CID_X" -H "Content-Type: application/json" -H "$AUTH" -d '{"name":"功能测试-客户X改","order_no":"TEST-001A","allowed_ips":"10.0.0.0/8","update_window":"00:00-23:59","enabled":1}' --max-time 6 > /dev/null
P "白名单拒绝(127.0.0.1)" curl -s -X POST "http://127.0.0.1:8091/apisix/plugin/jwt/sign?key=$KEY_X" -d "key=$KEY_X"
curl -sk -X PUT "https://127.0.0.1:8090/api/clients/$CID_X" -H "Content-Type: application/json" -H "$AUTH" -d '{"name":"功能测试-客户X改","order_no":"TEST-001A","allowed_ips":"127.0.0.1,10.0.0.0/8","update_window":"00:00-23:59","enabled":1}' --max-time 6 > /dev/null
P "CIDR放行后" curl -s -X POST "http://127.0.0.1:8091/apisix/plugin/jwt/sign?key=$KEY_X" -d "key=$KEY_X" -o /dev/null -w "%{http_code}"
echo ""
echo "===== D5. 更新时间窗口 ====="
curl -sk -X PUT "https://127.0.0.1:8090/api/clients/$CID_X" -H "Content-Type: application/json" -H "$AUTH" -d '{"name":"功能测试-客户X改","order_no":"TEST-001A","allowed_ips":"127.0.0.1","update_window":"23:58-23:59","enabled":1}' --max-time 6 > /dev/null
P "窗口外export" curl -s "http://127.0.0.1:8091/export?token=$TOK_X"
curl -sk -X PUT "https://127.0.0.1:8090/api/clients/$CID_X" -H "Content-Type: application/json" -H "$AUTH" -d '{"name":"功能测试-客户X改","order_no":"TEST-001A","allowed_ips":"127.0.0.1","update_window":"00:00-23:59","enabled":1}' --max-time 6 > /dev/null
P "窗口内export" curl -s "http://127.0.0.1:8091/export?token=$TOK_X"
echo ""
echo "===== D6. 禁用后全部拒绝 ====="
curl -sk -X PUT "https://127.0.0.1:8090/api/clients/$CID_X" -H "Content-Type: application/json" -H "$AUTH" -d '{"name":"功能测试-客户X改","order_no":"TEST-001A","allowed_ips":"127.0.0.1","update_window":"00:00-23:59","enabled":0}' --max-time 6 > /dev/null
P "禁用后sign"   curl -s -X POST "http://127.0.0.1:8091/apisix/plugin/jwt/sign?key=$KEY_X" -d "key=$KEY_X"
P "禁用后token查询" curl -s "http://127.0.0.1:8091/query?ip=198.51.100.7&token=$TOK_X"
curl -sk -X PUT "https://127.0.0.1:8090/api/clients/$CID_X" -H "Content-Type: application/json" -H "$AUTH" -d '{"name":"功能测试-客户X改","order_no":"TEST-001A","allowed_ips":"127.0.0.1","update_window":"00:00-23:59","enabled":1}' --max-time 6 > /dev/null
P "重新启用后"   curl -s -X POST "http://127.0.0.1:8091/apisix/plugin/jwt/sign?key=$KEY_X" -d "key=$KEY_X" -o /dev/null -w "%{http_code}"
echo ""
echo "===== D7. 更新记录累计 ====="
P "记录"         curl -sk "https://127.0.0.1:8090/api/clients/$CID_X/log" -H "$AUTH"
"""),
    ("⑤ 流影集成与 HTTPS", r"""
P(){ echo -n "$1: "; shift; "$@" --max-time 8 2>/dev/null; echo ""; }
TOKEN=$(curl -sk -X POST "https://127.0.0.1:8090/api/login" -H "Content-Type: application/json" -d '{"user":"admin","pass":"admin"}' --max-time 6 | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))")
AUTH="Authorization: Bearer $TOKEN"
CID_X=$(curl -sk "https://127.0.0.1:8090/api/clients" -H "$AUTH" --max-time 6 | python3 -c "import sys,json; d=json.load(sys.stdin); print([c['id'] for c in d['data'] if c['name']=='功能测试-客户X改'][0])")
KEY_X=$(curl -sk "https://127.0.0.1:8090/api/clients" -H "$AUTH" --max-time 6 | python3 -c "import sys,json; d=json.load(sys.stdin); print([c['cli_key'] for c in d['data'] if c['name']=='功能测试-客户X改'][0])")
echo "===== E1. HTTPS 证书 ====="
P "证书状态"     curl -sk "https://127.0.0.1:8090/api/cert"
echo ""
echo "===== E2. 流影威胁情报集成 ====="
COOKIE=/tmp/ly_cookie_ft.txt
rm -f $COOKIE
curl -s -X POST "http://127.0.0.1/d/auth" -d "auth_target=login&auth_user=admin&auth_pass=21232f297a57a5a743894a0e4a801fc3" -c $COOKIE --max-time 8 > /dev/null
P "threatconf保存" curl -s -X POST "http://127.0.0.1/d/threatconf" -d "op=save&api_key=&key=$KEY_X&tic_host=&tic_port=&tisrs_host=127.0.0.1&tisrs_port=8091" -b $COOKIE
P "threatinfo命中" curl -s "http://127.0.0.1/d/threatinfo?ip=198.51.100.7" -b $COOKIE
P "threatinfo未命中" curl -s "http://127.0.0.1/d/threatinfo?ip=203.0.113.99" -b $COOKIE
P "测试按钮"     curl -s -X POST "http://127.0.0.1/d/threatconf" -d "op=test" -b $COOKIE
echo ""
echo "===== E3. 服务端到端（当前配置） ====="
P "管理界面"     curl -sk -o /dev/null -w "%{http_code}" "https://127.0.0.1:8090/"
P "查询端口"     curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:8091/query"
echo ""
echo "===== E4. MySQL 数据状态 ====="
mysql -uroot -ppassword123 ti_server -e "SELECT (SELECT COUNT(*) FROM t_ioc) AS ioc, (SELECT COUNT(*) FROM t_client) AS client, (SELECT COUNT(*) FROM t_config) AS cfg;" 2>/dev/null
"""),
]

for label, cmd in cmds:
    print(f"\n{'='*20} {label} {'='*20}")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=400)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:800]}")

client.close()