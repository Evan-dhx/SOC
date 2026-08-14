import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("config_agent.pb 来源排查", r"""
echo "=== 1. 查找 config_agent.pb.h/cc ==="
find /root/SOC /home -name "config_agent.pb.*" 2>/dev/null | head -6
echo ""
echo "=== 2. config_agent.pb.h 中 Device 消息 ==="
PB=$(find /root/SOC -name "config_agent.pb.h" 2>/dev/null | head -1)
echo "文件: $PB"
grep -n "class Device\|set_psk\|set_interface\|set_filter" $PB 2>/dev/null | head -12
echo ""
echo "=== 3. Makefile protoc 规则 ==="
grep -B3 -A6 "\.pb\.cc" /root/SOC/ly_server_src/lib/Makefile 2>/dev/null | head -25
echo ""
echo "=== 4. config_agent.proto 历史备份 ==="
find /root/SOC -name "*.proto*" -path "*agent*" 2>/dev/null | head -5
ls /root/SOC/ly_server_src/common/pb_backup/ 2>/dev/null | head -20
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=240)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:800]}")

client.close()