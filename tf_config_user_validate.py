import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("ValidateRequest 完整", r"""
echo "=== 1. ValidateRequest 175-240 ==="
sed -n '175,240p' /root/SOC/ly_server_src/lib/config_user.cpp
echo ""
echo "=== 2. Failed() 定义 ==="
grep -n -A5 "Failed()" /root/SOC/ly_server_src/lib/config_class.cpp | head -15
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
