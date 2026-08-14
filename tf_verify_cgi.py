import paramiko
import sys
import time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Test web CGI interfaces", r"""
echo "=== 1. 测试 web CGI 接口 ==="
echo "--- /d/event ---"
curl -s "http://127.0.0.1/d/event" 2>&1 | head -c 200
echo ""
echo "--- /d/feature ---"
curl -s "http://127.0.0.1/d/feature" 2>&1 | head -c 200
echo ""
echo "--- /d/mo ---"
curl -s "http://127.0.0.1/d/mo" 2>&1 | head -c 200
echo ""
echo "--- /d/config ---"
curl -s "http://127.0.0.1/d/config" 2>&1 | head -c 200
echo ""
echo "--- /d/auth ---"
curl -s "http://127.0.0.1/d/auth" 2>&1 | head -c 200
echo ""
echo "=== 2. httpd 错误日志（最新 5 条） ==="
tail -5 /var/log/httpd/ly_error_log 2>/dev/null | grep -v "AH01264" | tail -3
"""),

    ("Run config_pusher full", r"""
echo "=== 3. 运行 config_pusher（完整配置） ==="
cd /Server/bin
timeout 60 ./config_pusher 2>&1 | head -10
echo "Exit: $?"
echo ""
echo "=== 4. config 文件 ==="
ls -la /Agent/data/config
echo "大小: $(stat -c%s /Agent/data/config) 字节"
echo ""
echo "=== 5. config 内容（文本格式） ==="
strings /Agent/data/config | head -20
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
