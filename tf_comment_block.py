import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("注释块定位", r"""
cd /root/SOC/ly_analyser_src/common
echo "=== 1. 370-395 行（找注释起止） ==="
sed -n '370,395p' mo_req.cpp
echo ""
echo "=== 2. 所有注释标记位置 ==="
grep -n "/\*" mo_req.cpp | head -5
echo "---"
grep -n "\*/" mo_req.cpp | head -5
echo ""
echo "=== 3. 本地副本对比（Windows 工作区） ==="
wc -l /root/SOC/ly_analyser_src/common/mo_req.cpp
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