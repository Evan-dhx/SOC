import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("mo_req.o 符号列表", r"""
cd /root/SOC/ly_analyser_src/common
echo "=== 1. mo_req.o 已定义符号（T） ==="
nm -C mo_req.o 2>/dev/null | grep " T " | head -25
echo ""
echo "=== 2. strings 检查 ==="
strings mo_req.o | grep -i "getmo" | head -3
echo ""
echo "=== 3. 重新编译并检查（单独文件测试） ==="
g++ -c -Wall -g -fPIC -std=c++17 -fpermissive -O2 -I. -I/usr/include -I/usr/local/include -I/usr/include/cgicc -I/usr/include/cppdb -o /tmp/moreq_test.o mo_req.cpp 2>&1 | head -5
nm -C /tmp/moreq_test.o | grep -i "getmo" | head -5
echo "退出码: $?"
echo ""
echo "=== 4. 检查 mo_req.h 的 namespace ==="
head -30 mo_req.h | grep -n "namespace"
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
