import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("ly_strings.h 验证与切换", r"""
echo "=== 1. ly_strings.h 存在性 ==="
ls -la /root/SOC/ly_analyser_src/common/ly_strings.h /root/SOC/ly_analyser_src/common/ly_strings.cpp 2>/dev/null
grep -n "trim" /root/SOC/ly_analyser_src/common/ly_strings.h 2>/dev/null | head -5
echo ""
echo "=== 2. 切换 include 并删除 strings.h ==="
sed -i 's|#include "../../common/strings.h"|#include "../../common/ly_strings.h"|' /root/SOC/ly_analyser_src/agent/handlers/actl.cpp /root/SOC/ly_analyser_src/agent/handlers/fsd.cpp
rm -f /root/SOC/ly_analyser_src/common/strings.h /root/SOC/ly_analyser_src/common/strings.cpp
grep -n "ly_strings.h" /root/SOC/ly_analyser_src/agent/handlers/actl.cpp /root/SOC/ly_analyser_src/agent/handlers/fsd.cpp
echo ""
echo "=== 3. 重新编译 actl + fsd ==="
cd /root/SOC/ly_analyser_src/agent/handlers
rm -f actl.o fsd.o actl fsd
make actl > /tmp/a.log 2>&1; echo "actl exit=$?"; ls -la actl 2>/dev/null
make fsd > /tmp/f.log 2>&1; echo "fsd exit=$?"; ls -la fsd 2>/dev/null
tail -3 /tmp/a.log; tail -3 /tmp/f.log
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=900)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()