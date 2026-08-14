import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("错误日志 + sctl/mo 源码分析", r"""
echo "=== 1. ly_error_log 最新 15 行 ==="
tail -15 /var/log/httpd/ly_error_log 2>/dev/null
echo ""
echo "=== 2. sctl 直接运行 ==="
echo 'devid: 1' | timeout 30 /Server/www/d/sctl 2>&1 | head -c 500
echo ""
echo "退出码: $?"
echo ""
echo "=== 3. mo.cpp 中 failed 输出点 ==="
grep -n "failed\|FAIL" /root/SOC/ly_server_src/server/mo.cpp | head -10
echo ""
echo "=== 4. mo 直接运行 ==="
echo 'devid: 1
starttime: 1786596300
endtime: 1786601400' | timeout 60 /Server/www/d/mo 2>&1 | head -c 500
echo ""
echo "退出码: $?"
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
