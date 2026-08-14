import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("server 目录 pb 头文件检查", r"""
echo "=== 1. server 目录下 .pb.h/.pb.cc ==="
ls -la /root/SOC/ly_server_src/server/*.pb.h /root/SOC/ly_server_src/server/*.pb.cc 2>/dev/null
echo ""
echo "=== 2. common 目录 pb 头文件 ==="
ls -la /root/SOC/ly_analyser_src/common/*.pb.h 2>/dev/null | head -20
echo ""
echo "=== 3. server 目录其他头文件 ==="
ls /root/SOC/ly_server_src/server/*.h 2>/dev/null
echo ""
echo "=== 4. mo.cpp 的 validate_request ==="
grep -n -B2 -A20 "validate_request" /root/SOC/ly_server_src/server/mo.cpp | head -50
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
