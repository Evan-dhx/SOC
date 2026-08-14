import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("config_user/bwlist SQL 检查", r"""
echo "=== 1. config_user.cpp SELECT ==="
grep -n "SELECT" /root/SOC/ly_server_src/lib/config_user.cpp | head -5
echo ""
echo "=== 2. config_bwlist.cpp SELECT ==="
grep -n "SELECT\|FROM" /root/SOC/ly_server_src/lib/config_bwlist.cpp | head -10
echo ""
echo "=== 3. 现有 t_user / t_blacklist 结构 ==="
mysql -uroot -ppassword123 server -e "SHOW CREATE TABLE t_user\G" 2>&1 | grep -E "^\s+\`|ENGINE" | head -20
echo "---"
mysql -uroot -ppassword123 server -e "SHOW CREATE TABLE t_blacklist\G" 2>&1 | grep -E "^\s+\`|ENGINE" | head -15
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
