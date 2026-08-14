import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Find config_pusher source", r"""
echo "=== 1. config_pusher 源码位置 ==="
find /root/SOC -name "config_pusher*" -type f 2>/dev/null | head -10
echo ""
echo "=== 2. config_updater 源码（agent 侧） ==="
ls -la /root/SOC/ly_analyser_src/agent/handlers/config_updater.cpp 2>/dev/null
echo ""
echo "=== 3. ly_server 源码位置 ==="
ls /root/SOC/ 2>/dev/null
echo ""
echo "=== 4. config_pusher 链接信息 ==="
ldd /Server/bin/config_pusher 2>&1 | grep -E "not found|common|protobuf" 
readelf -d /Server/bin/config_pusher | grep NEEDED
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
