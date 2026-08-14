import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("加密验证 + nfcapd 真实收流", r"""
cd /root/nftls_build
fuser -k 19995/tcp 19996/udp 9996/udp 19997/udp 2>/dev/null; sleep 2
mkdir -p flow_test
echo "===== 1. 启动独立 nfcapd(19997) + nftls server + client ====="
(setsid /Agent/bin/nfcapd -D -p 19997 -l /root/nftls_build/flow_test -z -b 127.0.0.1 -w >/dev/null 2>&1 &) >/dev/null 2>&1
sleep 1
(setsid /root/nftls_build/nftls -m server -l 127.0.0.1:19995 -r 127.0.0.1:19997 -p /root/nftls_build/test.psk -s /root/nftls_build/test.status >srv2.log 2>&1 </dev/null &) >/dev/null 2>&1
sleep 1
(setsid /root/nftls_build/nftls -m client -l 127.0.0.1:9996 -r 127.0.0.1:19995 -i 设备A -k key_A_0123456789abcdef >cli2.log 2>&1 </dev/null &) >/dev/null 2>&1
sleep 2
ps aux | grep -E "nfcapd -p 19997|nftls" | grep -v grep | awk '{print $2, $11, $12, $13, $14, $15}'
echo ""
echo "===== 2. 后台 tcpdump 抓 19995（8 秒，期间灌包） ====="
(setsid timeout 8 tcpdump -i lo -nn "port 19995" -w /tmp/tls_cap.pcap >/dev/null 2>&1 </dev/null &) >/dev/null 2>&1
sleep 1
python3 - <<'PYEOF'
import socket, struct, time
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# 模拟 tsensor NetFlow v9 导出流（30 个包，2 秒内）
for i in range(30):
    pkt = struct.pack(">HHIIII", 9, 1, 100+i, 2000+i, 0x11223344, i) + bytes(range(64))
    s.sendto(pkt, ("127.0.0.1", 9996))
    time.sleep(0.06)
print("已灌 30 个包")
PYEOF
sleep 8
echo ""
echo "===== 3. tcpdump 结果分析（19995 应为 TLS 密文） ====="
tcpdump -r /tmp/tls_cap.pcap -nn 2>/dev/null | head -5
echo "--- 明文 NetFlow v9 特征(0x0009)在 19995 出现次数 ---"
tcpdump -r /tmp/tls_cap.pcap -nn -XX 2>/dev/null | grep -c "0009 0001" || echo "0 (无明文特征, 加密生效)"
echo "--- TLS record 出现次数 ---"
tcpdump -r /tmp/tls_cap.pcap -nn -XX 2>/dev/null | grep -cE "16 03 03|17 03 03" || echo "0"
echo ""
echo "===== 4. nfcapd 收流落盘 ====="
ls -la flow_test/ | tail -3
echo ""
echo "===== 5. 明文端口对比（9996 上应看到明文 NetFlow） ====="
tcpdump -r /tmp/tls_cap.pcap -nn -XX 2>/dev/null | grep -c "0009 0001" ; echo "(上面为 19995 端口明文特征计数)"
fuser -k 19995/tcp 19996/udp 9996/udp 19997/udp 2>/dev/null
echo "已清理测试进程"
"""),
]

for label, cmd in cmds:
    print(f"\n{'='*20} {label} {'='*20}")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1200]}")

client.close()