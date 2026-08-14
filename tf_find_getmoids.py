import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("找 getMoIDs 定义", r"""
echo "=== 1. getMoIDs 定义位置 ==="
grep -rn "getMoIDs" /root/SOC/ly_analyser_src/common/*.cpp /root/SOC/ly_analyser_src/common/*.h 2>/dev/null | head -5
echo ""
echo "=== 2. libcommon.so 是否有该符号 ==="
nm -D /lib64/libcommon.so 2>/dev/null | grep "getMoIDs" | head -3
echo ""
echo "=== 3. 该函数所在文件是否已编译进 libcommon.a ==="
nm /root/SOC/ly_analyser_src/common/libcommon.a 2>/dev/null | grep "getMoIDs" | head -3
echo ""
echo "=== 4. mo_req.cpp 中函数列表 ==="
grep -n "^[a-z].*(" /root/SOC/ly_analyser_src/common/mo_req.cpp | head -15
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
