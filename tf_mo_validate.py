import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("mo_req.cpp validate + 强编 mo", r"""
cd /root/SOC/ly_server_src/server
echo "=== 1. validate_request 完整（mo_req.cpp 70-110） ==="
sed -n '70,115p' /root/SOC/ly_analyser_src/common/mo_req.cpp
echo ""
echo "=== 2. mo_req.cpp action 解析 ==="
grep -n -B2 -A8 "action" /root/SOC/ly_analyser_src/common/mo_req.cpp | head -40
echo ""
echo "=== 3. 强制重编译 mo ==="
rm -f mo
make mo 2>&1 | tail -3
echo ""
echo "=== 4. mo 符号检查 ==="
nm -u mo 2>/dev/null | grep -c "give_permission" || echo "0"
ls -la mo
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=600)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()
