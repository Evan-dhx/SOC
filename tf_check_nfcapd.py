import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Check nfcapd usage", r"""
echo "=== nfcapd help ==="
/Agent/bin/nfcapd -h 2>&1 | head -40
echo ""
echo "=== 尝试前台启动 ==="
pkill -f nfcapd 2>/dev/null
sleep 1
/Agent/bin/nfcapd -p 9995 -l /data/flow -z -b 0.0.0.0 > /tmp/nfcapd.log 2>&1 &
sleep 3
echo "--- 9995 监听检查 ---"
ss -tlnup | grep 9995 || echo "STILL NOT LISTENING"
echo "--- 进程 ---"
ps aux | grep nfcapd | grep -v grep
echo "--- 日志 ---"
cat /tmp/nfcapd.log 2>/dev/null
"""),

    ("Check nfcapd binary deps", r"""
echo "=== nfcapd ldd ==="
ldd /Agent/bin/nfcapd 2>&1 | grep -E "not found|=>"
echo ""
echo "=== 检查旧启动方式（flow_capd_launcher 找什么） ==="
grep -rn "nfcapd" /root/SOC/ly_analyser_src/agent/flow/*.cpp 2>/dev/null | grep -iE "system|exec|spawn|launch|cmd" | head -10
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
