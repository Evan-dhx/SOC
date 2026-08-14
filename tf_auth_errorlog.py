import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("ly_error_log + auth 二进制状态", r"""
echo "=== 1. ly_error_log 最近 30 行 ==="
tail -30 /var/log/httpd/ly_error_log 2>/dev/null
echo ""
echo "=== 2. auth 二进制 vs 源码时间 ==="
ls -la /Server/www/d/auth /root/SOC/ly_server_src/server/auth.cpp /root/SOC/ly_server_src/server/auth 2>/dev/null
echo ""
echo "=== 3. process() 登录逻辑（200-300 行） ==="
sed -n '200,300p' /root/SOC/ly_server_src/server/auth.cpp
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
