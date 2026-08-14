import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("sctl 500 诊断", r"""
echo "=== 1. ly_error_log 最新 8 行 ==="
tail -8 /var/log/httpd/ly_error_log 2>/dev/null
echo ""
echo "=== 2. sctl 直接运行 ==="
echo "op=get" | timeout 30 /Server/www/d/sctl 2>&1 | head -c 800
echo ""
echo "退出码: $?"
echo ""
echo "=== 3. sctl 二进制信息 ==="
ls -la /Server/www/d/sctl
ldd /Server/www/d/sctl 2>&1 | grep -E "common|protobuf|not found"
echo ""
echo "=== 4. sctl.cpp main/process ==="
grep -n "int main\|static void process\|ParseCtlReq" /root/SOC/ly_server_src/server/sctl.cpp | head -10
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
