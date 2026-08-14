import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("检查 /usr/local/include 旧头文件", r"""
echo "=== 1. /usr/local/include 下 pb 头文件 ==="
ls -la /usr/local/include/*.pb.h 2>/dev/null
echo ""
echo "=== 2. /usr/include 下 pb 头文件 ==="
ls -la /usr/include/*.pb.h 2>/dev/null
echo ""
echo "=== 3. 比对 ctl.pb.h 新旧 ==="
grep -c "Impl_" /usr/local/include/ctl.pb.h 2>/dev/null || echo "不存在"
grep -c "Impl_" /root/SOC/ly_analyser_src/common/ctl.pb.h 2>/dev/null
echo ""
echo "=== 4. sctl.cpp include 语句 ==="
grep -n "include.*pb.h\|include.*ctl" /root/SOC/ly_server_src/server/sctl.cpp | head -10
echo ""
echo "=== 5. mo.cpp include 语句 ==="
grep -n "include.*pb.h\|include.*mo" /root/SOC/ly_server_src/server/mo.cpp | head -10
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
