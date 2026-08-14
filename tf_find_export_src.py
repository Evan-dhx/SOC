import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Find export error source", r"""
echo "=== 1. tsensor 源码位置 ==="
ls /root/tsensor/ 2>/dev/null | head -20
find /root/tsensor -name "export.c" -o -name "export.cpp" 2>/dev/null
echo ""
echo "=== 2. export.c:904 附近代码 ==="
grep -rn "too many NetFlow flows per packet" /root/tsensor/ 2>/dev/null | head -3
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
