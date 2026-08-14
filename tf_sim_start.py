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

# Step A: 部署并启动模拟服务
cmd_a = f"""
pkill -f sim_ti_server.py 2>/dev/null
sleep 1
cat > /tmp/sim_ti_server.py <<'PYEOF'
{SIM_SERVER}
PYEOF
nohup setsid python3 /tmp/sim_ti_server.py > /tmp/sim_ti_server.log 2>&1 < /dev/null &
sleep 2
echo -n "模拟服务进程: "; pgrep -f sim_ti_server.py | head -1
curl -s -X POST "http://127.0.0.1:18090/apisix/plugin/jwt/sign?key=sim_key_2026" -d "key=sim_key_2026" --max-time 5
echo ""
curl -s -X POST "http://127.0.0.1:18090/apisix/plugin/jwt/sign?key=wrong_key" -d "key=wrong_key" --max-time 5 -o /dev/null -w "错误key状态码: %{{http_code}}\\n"
"""

stdin, stdout, stderr = client.exec_command(cmd_a, timeout=120)
print("[Step A: 模拟服务部署启动]")
print(stdout.read().decode('utf-8', errors='replace'))
err = stderr.read().decode('utf-8', errors='replace')
if err:
    print(f"STDERR: {err[:1000]}")

client.close()