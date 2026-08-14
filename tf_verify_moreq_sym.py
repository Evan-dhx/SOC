import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("符号验证", r"""
cd /root/SOC/ly_analyser_src/common
echo "=== 1. mo_req.o 中 getMoIDs ==="
nm mo_req.o | grep getMoIDs
echo ""
echo "=== 2. libcommon.a 成员列表（mo_req） ==="
ar t libcommon.a | grep mo_req
echo ""
echo "=== 3. libcommon.a 中 getMoIDs ==="
nm libcommon.a 2>/dev/null | grep -i getMoIDs | head -3
echo ""
echo "=== 4. libcommon.so 中 getMoIDs ==="
nm -D libcommon.so 2>/dev/null | grep -i getMoIDs | head -3
echo ""
echo "=== 5. mo_req.o 大小 ==="
ls -la mo_req.o
echo ""
echo "=== 6. getMoIDs 定义上下文（405-425 行） ==="
sed -n '405,425p' mo_req.cpp
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
