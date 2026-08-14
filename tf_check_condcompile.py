import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("条件编译检查", r"""
cd /root/SOC/ly_analyser_src/common
echo "=== 1. mo_req.cpp 411 行附近完整上下文（含条件编译） ==="
sed -n '400,430p' mo_req.cpp
echo ""
echo "=== 2. mo_req.h 中 getMoIDs 声明 ==="
grep -n -B2 -A2 "getMoID" mo_req.h
echo ""
echo "=== 3. mo_req.cpp 开头 30 行（include/define） ==="
head -30 mo_req.cpp
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