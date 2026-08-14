import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Deploy and test indexer", r"""
echo "=== Deploy new indexer ==="
cp /root/SOC/ly_analyser_src/agent/indexing/indexer /Agent/bin/indexer
chmod +x /Agent/bin/indexer
echo "Deployed: $(ls -lh /Agent/bin/indexer | awk '{print $5}')"
echo ""
echo "=== Test: indexer --help (was crashing before) ==="
cd /Agent/bin
timeout 5 ./indexer --help 2>&1 | head -20
echo "Exit: $?"
echo ""
echo "=== Test: indexer -v ==="
timeout 5 ./indexer -v 2>&1 | head -10
echo "Exit: $?"
"""),

    ("Start nfcapd on 9995", r"""
echo "=== Start nfcapd ==="
echo "--- 检查数据目录 ---"
ls -ld /data/flow/ 2>/dev/null || mkdir -p /data/flow
echo "--- 启动 nfcapd ---"
pkill -f "nfcapd" 2>/dev/null
sleep 1
nohup /Agent/bin/nfcapd -D -p 9995 -l /data/flow -z -b 0.0.0.0 > /tmp/nfcapd.log 2>&1 &
sleep 2
echo "--- 9995 监听检查 ---"
ss -tlnup | grep 9995
echo "--- nfcapd 进程 ---"
ps aux | grep nfcapd | grep -v grep
echo "--- nfcapd 日志 ---"
cat /tmp/nfcapd.log 2>/dev/null | head -10
"""),

    ("Test data flow with nfreplay", r"""
echo "=== 模拟流量测试 ==="
echo "--- 当前 9995 状态 ---"
ss -tlnup | grep 9995
echo ""
echo "--- 发送测试流（如果存在测试文件） ---"
find /data /tmp -name "*.nfcapd*" 2>/dev/null | head -5
echo ""
echo "--- 查找可用的流量样本 ---"
find /root/SOC -name "*.nfcapd*" -o -name "*.pcap" 2>/dev/null | head -5
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()
