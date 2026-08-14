import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("预处理定位", r"""
cd /root/SOC/ly_analyser_src/common
echo "=== 1. 预处理 getMoIDs 位置 ==="
g++ -E -std=c++17 -I. -I/usr/include -I/usr/local/include -I/usr/include/cgicc -I/usr/include/cppdb mo_req.cpp 2>/dev/null | grep -n "getMoIDs"
echo ""
echo "=== 2. moreq_test2.o 符号（完整 getmo 匹配） ==="
nm -C /tmp/moreq_test2.o | grep -i "getmo" | head -5
echo "nm 输出行数: $(nm /tmp/moreq_test2.o | wc -l)"
echo ""
echo "=== 3. 头文件是否被修改过（28-29 行是否就是这两个声明） ==="
sed -n '25,31p' mo_req.h
echo ""
echo "=== 4. mo_req.cpp 410-412 行（精确） ==="
sed -n '410,412p' mo_req.cpp | cat -A | head -5
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