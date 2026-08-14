import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Check t_device and push logic", r"""
echo "=== 1. t_device 表内容 ==="
mysql -e "SELECT * FROM server.t_device;" 2>/dev/null | head -10
echo ""
echo "=== 2. t_agent 表 ==="
mysql -e "SELECT * FROM server.t_agent;" 2>/dev/null | head -5
echo ""
echo "=== 3. config_pusher push() 逻辑（940-1030） ==="
sed -n '940,1030p' /root/SOC/ly_server_src/server/config_pusher.cpp
"""),

    ("Check feature/auth params", r"""
echo "=== 4. feature.cpp 参数要求 ==="
grep -n "Invalid Params\|400" /root/SOC/ly_server_src/server/feature.cpp | head -5
echo ""
echo "=== 5. auth.cpp 崩溃原因 ==="
grep -n "int main\|json\|parse" /root/SOC/ly_server_src/server/auth.cpp | head -10
echo ""
echo "=== 6. feature 带参数测试 ==="
curl -s "http://127.0.0.1/d/feature?action=get&devid=1&starttime=1786600200&endtime=1786600500" 2>&1 | head -c 300
echo ""
echo "=== 7. auth 带参数测试 ==="
curl -s "http://127.0.0.1/d/auth?action=login&username=admin&password=admin" 2>&1 | head -c 300
echo ""
tail -3 /var/log/httpd/ly_error_log 2>/dev/null
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
