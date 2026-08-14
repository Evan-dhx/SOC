import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("mo_req.cpp 函数头检查", r"""
cd /root/SOC/ly_analyser_src/common
echo "=== 1. 411 行前 3 行（函数头） ==="
sed -n '408,415p' mo_req.cpp
echo ""
echo "=== 2. mo_req.o 全部 getmo 相关符号（demangle） ==="
nm -C mo_req.o | grep -i "getmo" | head -5
echo ""
echo "=== 3. mo_req.cpp 是否在 411 行附近有条件编译 ==="
sed -n '395,412p' mo_req.cpp
echo ""
echo "=== 4. 文件行数与修改时间 ==="
wc -l mo_req.cpp
ls -la mo_req.cpp mo_req.o | awk '{print $6, $7, $8, $9}'
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
