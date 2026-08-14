import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("locinfo 防崩溃 + 重编译", r"""
cd /root/SOC/ly_server_src/server
echo "=== 1. ipip.hpp init 签名 ==="
grep -n "init\|static" /root/SOC/ly_analyser_src/common/ipip.hpp | head -10
echo ""
echo "=== 2. locinfo.cpp process() 完整 ==="
sed -n '50,90p' locinfo.cpp
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