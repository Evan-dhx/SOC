import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("View dbc.cpp connection", r"""
echo "=== dbc.cpp start_db_session ==="
grep -n -B3 -A25 "start_db_session" /root/SOC/ly_server_src/server/dbc.cpp | head -50
echo ""
echo "=== 连接参数来源 ==="
grep -n "getenv\|MYSQL\|DB_\|host\|password\|user\|dbname\|socket" /root/SOC/ly_server_src/server/dbc.cpp | head -20
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()
