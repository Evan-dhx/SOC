import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("模拟服务日志", r"""
echo "=== 1. 日志 ==="
cat /tmp/sim_ti_server.log 2>/dev/null
echo ""
echo "=== 2. 端口监听 ==="
ss -tlnp 2>/dev/null | grep 18090 || echo "18090 未监听"
echo ""
echo "=== 3. 进程详情 ==="
ps aux | grep sim_ti | grep -v grep | head -2
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=120)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()