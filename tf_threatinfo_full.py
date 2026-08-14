import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("threatinfo 完整逻辑", r"""
echo "=== 1. threatinfo.cpp main 剩余部分 ==="
sed -n '80,180p' /root/SOC/ly_server_src/server/threatinfo.cpp
echo ""
echo "=== 2. tic.h（威胁情报客户端库） ==="
cat /root/SOC/ly_analyser_src/common/tic.h 2>/dev/null | head -100
echo ""
echo "=== 3. threatinfopro.cpp 完整 ==="
cat /root/SOC/ly_server_src/server/threatinfopro.cpp 2>/dev/null | head -100
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