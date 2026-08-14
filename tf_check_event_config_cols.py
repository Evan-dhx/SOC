import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("config_event.cpp 全部表查询列", r"""
echo "=== 1. 各表 SELECT 语句 ==="
grep -n "SELECT \`id\`" /root/SOC/ly_server_src/lib/config_event.cpp | head -20
echo ""
echo "=== 2. icmp_tunnel / frn_trip / url_content 查询 ==="
grep -n -A2 "t_event_config_icmp_tunnel\|t_event_config_frn_trip\|t_event_config_url_content" /root/SOC/ly_server_src/lib/config_event.cpp | grep -E "SELECT|FROM" | head -10
echo ""
echo "=== 3. 官方 t_event_action 定义（SQL 300-375 行） ==="
sed -n '300,375p' /root/SOC/ly_server_src/../ly_server_src/../../../../tf_extract_db/db.server.v1.1.231123/db.server.v1.1.231123.opensource.sql 2>/dev/null | head -5
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
