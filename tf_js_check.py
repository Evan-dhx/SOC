import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("JS 完整性 + 前端逻辑", r"""
echo "=== 1. main chunk JS 与备份的 md5 对比 ==="
md5sum /Server/www/ui/static/js/main.ff156c89.chunk.js /Server/www/ui/static/js/main.ff156c89.chunk.js.bak /Server/www/ui/static/js/main.ff156c89.chunk.js.modified_bak 2>/dev/null
echo ""
echo "=== 2. 所有 JS 中'未登录'出现位置 ==="
grep -l "未登录" /Server/www/ui/static/js/*.js 2>/dev/null
echo ""
echo "=== 3. 前端请求 URL 拼接（编译版中 baseUrl 相关） ==="
grep -o "baseUrl[^,}]*" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -3
grep -o "config[.]baseUrl[^;]*" /Server/www/ui/static/js/main.ff156c89.chunk.js 2>/dev/null | head -3
echo ""
echo "=== 4. 无 cookie 时 auth 返回格式（300） ==="
curl -s "http://10.10.102.220/d/feature?action=get&devid=1" --max-time 30 2>&1 | head -c 200
echo ""
echo ""
echo "=== 5. 带无效 cookie 访问 ==="
curl -s "http://10.10.102.220/d/feature?action=get&devid=1" -H "Cookie: SESSION_ID=deadbeefdeadbeefdeadbeefdeadbeef" --max-time 30 2>&1 | head -c 200
echo ""
echo ""
echo "=== 6. Set-Cookie 响应头完整内容（含 Path） ==="
curl -s -D - -o /dev/null -X POST "http://10.10.102.220/d/auth" -d "auth_target=login&auth_user=admin&auth_pass=21232f297a57a5a743894a0e4a801fc3" --max-time 30 2>&1 | grep -i "set-cookie"
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