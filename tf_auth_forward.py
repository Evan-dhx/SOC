import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("auth 转发执行逻辑", r"""
echo "=== 1. auth.cpp 中 popen/转发/执行目标 ==="
grep -n "popen\|auth_target\|SERVER_WWW_DIR\|forward\|exec" /root/SOC/ly_server_src/server/auth.cpp | head -25
echo ""
echo "=== 2. main 中转发部分（460-560 行） ==="
sed -n '460,560p' /root/SOC/ly_server_src/server/auth.cpp
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