import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("白屏诊断", r"""
echo "=== 1. 最近 2 小时修改的文件（排除日志） ==="
find /Server /root/SOC/ly_server_src /root/SOC/ly_analyser_src -newermt '-2 hours' -type f 2>/dev/null | grep -v "\.log\|ly_error_log\|/tmp/" | head -30
echo ""
echo "=== 2. /Server/www 结构 ==="
ls -la /Server/www/ 2>/dev/null
echo "--- /Server/www/ui ---"
ls -la /Server/www/ui/ 2>/dev/null | head -10
echo ""
echo "=== 3. 页面响应 ==="
curl -s -o /dev/null -w "/: %{http_code}\n" "http://127.0.0.1/" --max-time 15
curl -s -o /dev/null -w "/ui/: %{http_code}\n" "http://127.0.0.1/ui/" --max-time 15
curl -s "http://127.0.0.1/ui/" --max-time 15 2>&1 | head -c 500
echo ""
echo "=== 4. httpd 状态 ==="
systemctl status httpd 2>&1 | head -5
echo ""
echo "=== 5. 最新错误日志 ==="
tail -15 /var/log/httpd/ly_error_log 2>/dev/null | grep -v "AH00489\|AH00094\|AH02282\|AH01232\|AH00492\|suexec\|mpm_event\|AH02284" | tail -10
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