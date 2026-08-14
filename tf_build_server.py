import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("编译 ly_server config_agent.so + config_pusher", r"""
echo "=== 1. config_agent.so ==="
cd /root/SOC/ly_server_src/lib
make config_agent.so > /tmp/ca.log 2>&1; echo "exit=$?"
ls -la config_agent.so 2>/dev/null
tail -3 /tmp/ca.log
echo ""
echo "=== 2. config_pusher ==="
cd /root/SOC/ly_server_src/server
make config_pusher > /tmp/cp.log 2>&1; echo "exit=$?"
ls -la config_pusher 2>/dev/null
tail -3 /tmp/cp.log
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=1200)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1200]}")

client.close()