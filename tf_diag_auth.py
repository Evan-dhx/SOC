import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("auth 和 extract_event 诊断", r"""
echo "=== 1. auth CGI 直接运行测试 ==="
echo "username=admin&password=admin" | REMOTE_ADDR=127.0.0.1 REQUEST_METHOD=POST CONTENT_TYPE=application/x-www-form-urlencoded CONTENT_LENGTH=40 timeout 30 /Server/www/d/auth 2>&1 | head -c 1000
echo ""
echo "退出码: $?"
echo ""
echo "=== 2. extract_event 直接运行 ==="
echo 'devid: 1' | timeout 30 /Agent/cmd/extract_event 2>&1 | head -c 1000
echo ""
echo "退出码: $?"
echo ""
echo "=== 3. mo CGI 直接运行 ==="
curl -s "http://127.0.0.1/d/mo?action=get&devid=1&starttime=1786596300&endtime=1786601400&dbg=1" --max-time 60 2>&1 | head -c 1000
echo ""
echo "=== 4. / 403 原因 ==="
curl -s -o /dev/null -w "%{http_code}\n" "http://127.0.0.1/index.html" --max-time 15
ls -la /var/www/html/ 2>/dev/null | head -5
echo ""
echo "=== 5. auth.cpp 源码位置 ==="
ls /root/SOC/ly_server_src/server/auth* 2>/dev/null
grep -rn "auth" /root/SOC/ly_server_src/server/Makefile 2>/dev/null | head -5
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=240)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()
