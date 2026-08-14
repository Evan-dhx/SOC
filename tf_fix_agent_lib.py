import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Update /Agent/lib libcommon", r"""
echo "=== 1. /Agent/lib 当前状态 ==="
ls -la /Agent/lib/ 2>/dev/null
echo ""
echo "=== 2. 备份并更新 libcommon.so ==="
cp /Agent/lib/libcommon.so /Agent/lib/libcommon.so.bak_old 2>/dev/null
cp /lib64/libcommon.so /Agent/lib/libcommon.so
ldconfig
echo "已更新"
ls -la /Agent/lib/libcommon.so
echo ""
echo "=== 3. 测试 config_updater CGI ==="
curl -s -X POST -d "test" http://127.0.0.1:10081/config_updater -w "\nHTTP:%{http_code}\n" 2>&1 | head -8
echo ""
echo "=== 4. 测试 web CGI（config 接口） ==="
curl -s "http://127.0.0.1/d/config?action=get" 2>&1 | head -5
echo ""
echo "=== 5. httpd 错误日志最新 ==="
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
