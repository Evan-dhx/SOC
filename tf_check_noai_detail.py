import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("深入分析 flow_filter_noai", r"""
echo "=== 1. 哪些 Makefile 引用 flow_filter_noai ==="
grep -rn "flow_filter_noai" /root/SOC/ly_analyser_src --include="Makefile*" 2>/dev/null
echo ""
echo "=== 2. port_scan_filter.o 引用的 FeatureRecord 符号 ==="
nm /root/SOC/ly_analyser_src/agent/flow/port_scan_filter.o 2>/dev/null | grep -E "U _ZN7feature.*FeatureRecord|U _ZN7feature.*FeatureResponse" | head -10
echo ""
echo "=== 3. flow_filter_noai.a 时间戳 ==="
ls -la /root/SOC/ly_analyser_src/agent/flow/flow_filter_noai.a /root/SOC/ly_analyser_src/agent/flow/libflow_filter.so 2>/dev/null
echo ""
echo "=== 4. 3.21.9 头文件中 FeatureRecord 构造函数声明 ==="
grep -n "FeatureRecord();\|FeatureRecord() :\|inline FeatureRecord" /root/SOC/ly_analyser_src/common/feature.pb.h | head -5
echo ""
echo "=== 5. indexer 在哪个目录编译 ==="
find /root/SOC/ly_analyser_src -name "indexer*" -type f 2>/dev/null | head -5
grep -rn "indexer" /root/SOC/ly_analyser_src/agent/Makefile 2>/dev/null | head -10
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=180)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()
