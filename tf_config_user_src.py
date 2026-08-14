import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("config_user.cpp 分析", r"""
echo "=== 1. Process 函数 ==="
grep -n "void Process\|::Process\|op_get\|op_add\|switch" /root/SOC/ly_server_src/lib/config_user.cpp | head -15
echo ""
echo "=== 2. op_get 完整（300-400） ==="
sed -n '300,400p' /root/SOC/ly_server_src/lib/config_user.cpp
echo ""
echo "=== 3. Process 定义（找行号） ==="
grep -n "Process(cgicc::Cgicc" /root/SOC/ly_server_src/lib/config_user.cpp /root/SOC/ly_server_src/lib/config_class.h | head -5
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
