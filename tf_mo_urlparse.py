import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("mo_req.cpp URL 解析", r"""
echo "=== 1. mo_req.cpp 全部函数 ==="
grep -n "static\|void\|bool\|Parse" /root/SOC/ly_analyser_src/common/mo_req.cpp | head -20
echo ""
echo "=== 2. ParseMoReqFromUrlParams 完整 ==="
grep -n -A40 "ParseMoReqFromUrlParams" /root/SOC/ly_analyser_src/common/mo_req.cpp | head -55
echo ""
echo "=== 3. cgi( 调用 ==="
grep -n "cgi(" /root/SOC/ly_analyser_src/common/mo_req.cpp | head -20
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
