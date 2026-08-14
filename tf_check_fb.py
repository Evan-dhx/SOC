import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Check fb.c status", r"""
echo "=== 1. fb.c 是否存在 ==="
ls -la /root/tsensor/fb.c /root/tsensor/.libs/fb.o /root/tsensor/fb.o 2>&1
echo ""
echo "=== 2. fb.c 内容概要 ==="
head -30 /root/tsensor/fb.c 2>/dev/null
echo ""
echo "=== 3. Makefile 中 fb 相关 ==="
grep -n "fb" /root/tsensor/Makefile | head -10
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
