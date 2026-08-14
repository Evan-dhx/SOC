import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("event.cpp 查询逻辑 + t_event_data", r"""
echo "=== 1. event.cpp process 函数体 ==="
sed -n '192,260p' /root/SOC/ly_server_src/server/event.cpp
echo ""
echo "=== 2. event.cpp SQL ==="
grep -n "SELECT\|FROM\|t_event" /root/SOC/ly_server_src/server/event.cpp | head -15
echo ""
echo "=== 3. t_event_data 表数据量 ==="
mysql -uroot -ppassword123 server -e "SELECT COUNT(*) AS cnt FROM t_event_data; SELECT COUNT(*) AS cnt2 FROM t_event_action;" 2>&1 | head -10
echo ""
echo "=== 4. indexer 是否生成过事件 ==="
find /Agent/data/eventdb -type f 2>/dev/null | head -5
echo ""
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
