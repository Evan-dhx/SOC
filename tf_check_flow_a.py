import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Check flow directory archives", r"""
echo "=== Flow directory .a files ==="
ls -lh /root/SOC/ly_analyser_src/agent/flow/*.a 2>/dev/null
echo ""
echo "=== Check flow_filter_full.a content ==="
ar t /root/SOC/ly_analyser_src/agent/flow/flow_filter_full.a 2>/dev/null | head -30
echo ""
echo "=== Check flow_filter.a content ==="
ar t /root/SOC/ly_analyser_src/agent/flow/flow_filter.a 2>/dev/null | head -30
"""),

    ("Check flow Makefile for flow_filter_full target", r"""
echo "=== flow Makefile targets ==="
grep -n "flow_filter\|abi0\|_full" /root/SOC/ly_analyser_src/agent/flow/Makefile | head -20
echo ""
echo "=== Check for abi0 build rules ==="
grep -n "abi0\|CXX11_ABI" /root/SOC/ly_analyser_src/agent/flow/Makefile | head -10
"""),

    ("Check timestamps", r"""
echo "=== Timestamps ==="
stat -c "%y %n" /root/SOC/ly_analyser_src/agent/flow/flow_filter.a /root/SOC/ly_analyser_src/agent/flow/flow_filter_full.a 2>/dev/null
echo ""
echo "=== Who references flow_filter_full ==="
grep -rn "flow_filter_full" /root/SOC/ly_analyser_src/agent/indexing/Makefile /root/SOC/ly_analyser_src/agent/flow/Makefile 2>/dev/null
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)

client.close()
