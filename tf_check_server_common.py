import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("检查 ly_server_src/common", r"""
echo "=== 1. ly_server_src/common 内容 ==="
ls -la /root/SOC/ly_server_src/common/ | head -30
echo ""
echo "=== 2. config_mo.cpp 的 include ==="
head -20 /root/SOC/ly_server_src/lib/config_mo.cpp | grep -n "include"
echo ""
echo "=== 3. 两个 common 的 mo.pb.h 对比 ==="
ls -la /root/SOC/ly_server_src/common/mo.pb.h /root/SOC/ly_analyser_src/common/mo.pb.h 2>/dev/null
grep -c "SetNoArena" /root/SOC/ly_server_src/common/mo.pb.h 2>/dev/null
grep -c "SetNoArena" /root/SOC/ly_analyser_src/common/mo.pb.h 2>/dev/null
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
