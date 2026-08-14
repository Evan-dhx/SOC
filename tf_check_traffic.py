import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Check traffic on port 9995", r"""
echo "=== 1. tcpdump 抓 9995 端口 10 秒 ==="
timeout 10 tcpdump -i any -c 20 udp port 9995 2>&1 | head -25
echo "Capture done"
"""),

    ("Check nfcapd packet stats", r"""
echo "=== 2. nfcapd 收到多少包 ==="
cat /proc/213235/net/snmp 2>/dev/null | head -5
echo ""
echo "=== 3. nfcapd stat 文件 ==="
ls -la /data/flow/nfstat* 2>/dev/null
nfdump -s /data/flow/nfstat* 2>/dev/null | head -20
"""),

    ("Test with nfreplay loopback", r"""
echo "=== 4. 用 nfreplay 本地回环测试 ==="
# 用已有的 flow 文件回放（如果有）
ls /data/flow/*.nfcapd* 2>/dev/null | head -5
echo ""
echo "--- 检查是否有可回放文件 ---"
find /data /tmp /root -name "*.nfcapd*" -size +1k 2>/dev/null | grep -v current | head -5
echo ""
echo "--- 生成测试流并回放 ---"
# 用 nfdump 转换现有小文件回放
ls -la /data/flow/
"""),

    ("Check user traffic source hints", r"""
echo "=== 5. 检查是否有其他进程连 9995 ==="
ss -tunap | grep 9995 | head -10
echo ""
echo "=== 6. 防火墙状态 ==="
firewall-cmd --state 2>/dev/null
iptables -L -n 2>/dev/null | head -15
echo ""
echo "=== 7. 服务器 IP ==="
ip addr show | grep -E "inet " | head -5
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
