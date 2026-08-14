import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("auth.cpp 中所有 SQL 语句", r"""
echo "=== 1. auth.cpp 所有 SQL ==="
grep -n "SELECT\|INSERT\|UPDATE\|DELETE\|FROM\|INTO" /root/SOC/ly_server_src/server/auth.cpp | head -30
echo ""
echo "=== 2. check_user_pass 完整（430-520） ==="
sed -n '430,530p' /root/SOC/ly_server_src/server/auth.cpp
echo ""
echo "=== 3. 其他 CGI 是否也引用 t_user ==="
grep -rn "t_user" /root/SOC/ly_server_src/server/*.cpp | head -10
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
