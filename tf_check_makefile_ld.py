import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Makefile LDFLAGS + .o 时间戳", r"""
echo "=== 1. server Makefile 完整 ==="
cat /root/SOC/ly_server_src/server/Makefile
echo ""
echo "=== 2. server .o 文件时间 ==="
ls -la /root/SOC/ly_server_src/server/*.o 2>/dev/null | awk '{print $6, $7, $8, $9}'
echo ""
echo "=== 3. validate_request 位置 ==="
grep -rn "validate_request" /root/SOC/ly_server_src/server/mo.cpp /root/SOC/ly_analyser_src/common/mo_req.cpp 2>/dev/null | head -5
echo ""
echo "=== 4. sctl.o 引用的符号 ==="
nm /root/SOC/ly_server_src/server/sctl.o 2>/dev/null | grep "give_permission" | head -3
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
