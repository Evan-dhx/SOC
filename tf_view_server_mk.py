import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("View ly_server Makefile", r"""
echo "=== 1. ly_server 目录结构 ==="
ls /root/SOC/ly_server_src/
ls /root/SOC/ly_server_src/server/ | head -20
echo ""
echo "=== 2. Makefile ==="
cat /root/SOC/ly_server_src/server/Makefile 2>/dev/null | head -60
echo ""
echo "=== 3. 编译参数检查 ==="
grep -E "CXXFLAGS|INCS|LDLIBS|CXX=" /root/SOC/ly_server_src/server/Makefile 2>/dev/null | head -10
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
