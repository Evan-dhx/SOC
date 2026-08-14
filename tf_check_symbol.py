import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Check ComposeReqFilter symbol", r"""
echo "=== Check symbol in libcommon.a ==="
nm /root/SOC/ly_analyser_src/common/libcommon.a 2>/dev/null | grep -i "ComposeReqFilter"
echo ""
echo "=== Check in topn_req.o ==="
nm /root/SOC/ly_analyser_src/common/topn_req.o 2>/dev/null | grep -i "ComposeReqFilter"
echo ""
echo "=== Check topn_req.o in archive ==="
ar t /root/SOC/ly_analyser_src/common/libcommon.a | grep topn
echo ""
echo "=== Check source ==="
grep -n "ComposeReqFilter" /root/SOC/ly_analyser_src/common/topn_req.cpp /root/SOC/ly_analyser_src/common/topn_req.h 2>/dev/null
"""),

    ("Check installed libcommon vs source libcommon", r"""
echo "=== Compare timestamps ==="
stat -c "%y %n" /lib64/libcommon.so /root/SOC/ly_analyser_src/common/libcommon.so /root/SOC/ly_analyser_src/common/libcommon.a 2>/dev/null
echo ""
echo "=== Check which libcommon the linker finds ==="
ldconfig -p | grep libcommon
echo ""
echo "=== Check symbol in installed so ==="
nm -D /lib64/libcommon.so 2>/dev/null | grep -i "ComposeReqFilter"
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)

client.close()
