import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("api_set 定义位置", r"""
echo "=== 1. api_set 定义 ==="
grep -rn "api_set" /root/SOC/ly_server_src/server/auth.cpp | head -5
echo ""
echo "=== 2. 定义内容 ==="
grep -n -B2 -A15 "set<string> api_set\|unordered_set<string> api_set\|api_set =" /root/SOC/ly_server_src/server/auth.cpp | head -30
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