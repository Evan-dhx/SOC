import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

SIM_SERVER = r'''
import http.server, urllib.parse, json

class H(http.server.BaseHTTPRequestHandler):
    def _read_body(self):
        try:
            n = int(self.headers.get('Content-Length', 0))
            return self.rfile.read(n) if n else b''
        except Exception:
            return b''

    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        self._read_body()
        if u.path == '/apisix/plugin/jwt/sign':
            key = q.get('key', [''])[0]
            if key == 'sim_key_2026':
                body = b'{"token":"sim_jwt_abc123"}'
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                body = b'{"code":401,"msg":"invalid key"}'
                self.send_response(401)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            return
        # 模拟威胁情报查询接口（ti_url 为空时请求根路径）
        if q.get('jwt', [''])[0]:
            resp = [{"ip": q.get('ip', [''])[0], "threat": "botnet",
                     "score": 95, "tag": "模拟恶意IP", "jwt_ok": True}]
            body = json.dumps(resp).encode()
            self.send_response(200)
        else:
            body = b'{"code":403,"msg":"token invalid"}'
            self.send_response(403)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass

http.server.HTTPServer(('0.0.0.0', 18090), H).serve_forever()
'''

cmds = [
    ("模拟威胁情报服务 + 全链路测试", f"""
echo "=== 1. 部署模拟服务 ==="
cat > /tmp/sim_ti_server.py <<'PYEOF'
{SIM_SERVER}
PYEOF
pkill -f sim_ti_server.py 2>/dev/null; sleep 1
nohup python3 /tmp/sim_ti_server.py > /tmp/sim_ti_server.log 2>&1 &
sleep 1
echo -n "模拟服务进程: "; pgrep -f sim_ti_server.py | head -1
echo ""
echo "=== 2. 本地自测模拟服务（JWT 换取） ==="
curl -s -X POST "http://127.0.0.1:18090/apisix/plugin/jwt/sign?key=sim_key_2026" -d "key=sim_key_2026" --max-time 5
echo ""
curl -s -X POST "http://127.0.0.1:18090/apisix/plugin/jwt/sign?key=wrong_key" -d "key=wrong_key" --max-time 5 -o /dev/null -w "错误key状态码: %{{http_code}}\\n"
echo ""
echo "=== 3. 登录 ==="
COOKIE=/tmp/ly_cookie_sim.txt
rm -f $COOKIE
curl -s -X POST "http://127.0.0.1/d/auth" -d "auth_target=login&auth_user=admin&auth_pass=21232f297a57a5a743894a0e4a801fc3" -c $COOKIE --max-time 30
echo ""
echo ""
echo "=== 4. 模拟前：未配置状态 ==="
echo -n "threatconf get: "; curl -s "http://127.0.0.1/d/threatconf?op=get" -b $COOKIE --max-time 30
echo ""
echo -n "threatinfo: "; curl -s "http://127.0.0.1/d/threatinfo?ip=1.2.3.4" -b $COOKIE --max-time 30
echo ""
echo ""
echo "=== 5. 模拟 UI 保存（threatconf op=save） ==="
curl -s -X POST "http://127.0.0.1/d/threatconf" -d "op=save&api_key=&key=sim_key_2026&tic_host=&tic_port=&tisrs_host=127.0.0.1&tisrs_port=18090" -b $COOKIE --max-time 30
echo ""
echo ""
echo "=== 6. 保存后 get 回显验证 ==="
curl -s "http://127.0.0.1/d/threatconf?op=get" -b $COOKIE --max-time 30
echo ""
echo ""
echo "=== 7. 测试按钮（op=test）→ 应 200 连通正常 ==="
curl -s -X POST "http://127.0.0.1/d/threatconf" -d "op=test" -b $COOKIE --max-time 30
echo ""
echo ""
echo "=== 8. 核心验证：threatinfo 走通模拟服务 ==="
curl -s "http://127.0.0.1/d/threatinfo?ip=1.2.3.4" -b $COOKIE --max-time 30
echo ""
echo ""
echo "=== 9. 错误 key 测试（改错 key 后 test） ==="
curl -s -X POST "http://127.0.0.1/d/threatconf" -d "op=save&api_key=&key=wrong_key&tic_host=&tic_port=&tisrs_host=127.0.0.1&tisrs_port=18090" -b $COOKIE --max-time 30 > /dev/null
curl -s -X POST "http://127.0.0.1/d/threatconf" -d "op=test" -b $COOKIE --max-time 30
echo ""
echo ""
echo "=== 10. 恢复正确配置 + 清理 ==="
curl -s -X POST "http://127.0.0.1/d/threatconf" -d "op=save&api_key=&key=sim_key_2026&tic_host=&tic_port=&tisrs_host=127.0.0.1&tisrs_port=18090" -b $COOKIE --max-time 30 > /dev/null
curl -s "http://127.0.0.1/d/threatinfo?ip=8.8.8.8" -b $COOKIE --max-time 30
echo ""
pkill -f sim_ti_server.py 2>/dev/null
sleep 1
echo -n "模拟服务已停止: "; pgrep -f sim_ti_server.py | wc -l
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