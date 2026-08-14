import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("编译产物验证", r"""
cd /root/SOC/ly_analyser_src/common
echo "=== 1. /tmp/moreq_test.o 是否存在 ==="
ls -la /tmp/moreq_test.o 2>&1
echo ""
echo "=== 2. 直接编译（完整输出） ==="
g++ -c -g -std=c++17 -fpermissive -O2 -I. -I/usr/include -I/usr/local/include -I/usr/include/cgicc -I/usr/include/cppdb -o /tmp/moreq_test2.o mo_req.cpp
echo "g++ 退出码: $?"
ls -la /tmp/moreq_test2.o
echo ""
echo "=== 3. 预处理检查 getMoIDs ==="
g++ -E -std=c++17 -I. -I/usr/include -I/usr/local/include -I/usr/include/cgicc -I/usr/include/cppdb mo_req.cpp 2>/dev/null | grep -c "getMoIDs"
echo ""
echo "=== 4. 测试最小程序 ==="
cat > /tmp/test_mo.cpp <<'EOF'
#include "mo_req.h"
namespace mo {
std::vector<u32> getMoIDs(cppdb::session* sql, const u32 groupid, u32 devid){ return {}; }
}
EOF
g++ -c -g -std=c++17 -I. -I/usr/include -I/usr/local/include -I/usr/include/cgicc -I/usr/include/cppdb -o /tmp/test_mo.o /tmp/test_mo.cpp
echo "编译退出码: $?"
nm -C /tmp/test_mo.o | grep getMoIDs
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