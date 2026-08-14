import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Check httpd error log", r"""
echo "=== ly_error_log 最新 ==="
tail -20 /var/log/httpd/ly_error_log 2>/dev/null
echo ""
echo "=== 直接运行 config_updater 测试 ==="
cd /Agent/cmd
REMOTE_ADDR=127.0.0.1 REQUEST_METHOD=POST CONTENT_LENGTH=4 ./config_updater <<< "test" 2>&1 | head -10
echo "Exit: $?"
echo ""
echo "=== 手动 POST 测试（看 stderr） ==="
curl -s -X POST -d "test" http://127.0.0.1:10081/config_updater 2>&1 | head -5
sleep 1
tail -5 /var/log/httpd/ly_error_log 2>/dev/null
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()
