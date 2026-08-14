import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("tic 客户端库", r"""
echo "=== 1. tic.h 位置与内容 ==="
find /root/SOC -name "tic.h" -o -name "tic.cpp" 2>/dev/null | head -5
echo "---"
cat /root/SOC/ly_analyser_src/common/tic.h 2>/dev/null
echo ""
echo "=== 2. threatinfopro.cpp 剩余（远程请求部分） ==="
sed -n '100,200p' /root/SOC/ly_server_src/server/threatinfopro.cpp
echo ""
echo "=== 3. tic.conf 是否存在 ==="
ls -la /Server/etc/tic.conf /Server/etc/tisrs.conf 2>&1
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