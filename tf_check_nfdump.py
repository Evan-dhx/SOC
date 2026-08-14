import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Check nfdump deps and build", r"""
echo "=== 1. nfdump NEEDED ==="
readelf -d /Agent/bin/nfdump | grep NEEDED
echo ""
echo "=== 2. nfdump 源码位置 ==="
ls /root/SOC/ly_analyser_src/nfdump/ | head -20
echo ""
echo "=== 3. nfdump Makefile 或 configure ==="
ls /root/SOC/ly_analyser_src/nfdump/Makefile 2>/dev/null && head -40 /root/SOC/ly_analyser_src/nfdump/Makefile
echo ""
echo "=== 4. agent/dump 目录（libnfdump.a） ==="
ls -la /root/SOC/ly_analyser_src/agent/dump/ | head -20
echo ""
echo "=== 5. nfdump bin 目录源码 ==="
ls /root/SOC/ly_analyser_src/nfdump/bin/ 2>/dev/null | head -20
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
