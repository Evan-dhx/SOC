import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("View config_updater.cpp", r"""
echo "=== config_updater.cpp 完整 ==="
cat /root/SOC/ly_analyser_src/agent/handlers/config_updater.cpp
echo ""
echo "=== t_agent 表 ==="
mysql -e "SELECT * FROM server.t_agent;" 2>/dev/null | head -10
echo ""
echo "=== 10081 端口 ==="
ss -tlnp | grep 10081
echo ""
echo "=== config_updater 进程 ==="
ps aux | grep "[c]onfig_updater" | head -3
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
