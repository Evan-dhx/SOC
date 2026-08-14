import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Check tsensor -m parameter", r"""
echo "=== tsensor 帮助（-m 相关） ==="
/usr/local/bin/tsensor -h 2>&1 | grep -iE "^-m|flows per|packet|export" | head -10
echo ""
echo "=== 完整帮助（关键部分） ==="
/usr/local/bin/tsensor -h 2>&1 | head -60
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()
