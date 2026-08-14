import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("查看 Apache 错误日志", r"""
echo "=== 1. httpd error_log 最近 extract 相关 ==="
tail -30 /var/log/httpd/error_log 2>/dev/null | grep -i "extract\|segfault\|error" | tail -15
echo ""
echo "=== 2. error_log 最后 10 行 ==="
tail -10 /var/log/httpd/error_log 2>/dev/null
echo ""
echo "=== 3. handlers Makefile 现状 ==="
cat /root/SOC/ly_analyser_src/agent/handlers/Makefile 2>/dev/null | head -60
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
