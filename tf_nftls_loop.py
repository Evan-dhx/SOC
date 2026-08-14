import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("nftls 单机环回测试", r"""
cd /root/nftls_build
fuser -k 19995/tcp 19996/udp 19997/udp 9996/udp 9997/udp 9998/udp 2>/dev/null; sleep 2
echo "===== 1. 准备 psk 文件与测试 UDP 接收端 ====="
cat > test.psk <<'EOF'
设备A:key_A_0123456789abcdef
设备B:key_B_0123456789abcdef
EOF
cat > /tmp/udp_dump.py <<'PYEOF'
import socket, sys, struct
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("127.0.0.1", 19996))
count = 0
while True:
    data, addr = s.recvfrom(65535)
    count += 1
    print(f"UDP包#{count} len={len(data)} head={data[:8].hex()}", flush=True)
PYEOF
echo ""
echo "===== 2. 启动 nftls server + client ====="
(setsid /root/nftls_build/nftls -m server -l 127.0.0.1:19995 -r 127.0.0.1:19996 -p /root/nftls_build/test.psk -s /root/nftls_build/test.status >/root/nftls_build/srv.log 2>&1 </dev/null &) >/dev/null 2>&1
sleep 1
(setsid /root/nftls_build/nftls -m client -l 127.0.0.1:9996 -r 127.0.0.1:19995 -i 设备A -k key_A_0123456789abcdef >/root/nftls_build/cli.log 2>&1 </dev/null &) >/dev/null 2>&1
sleep 2
echo "进程:"; ps aux | grep nftls | grep -v grep | awk '{print $2, $11, $12, $13, $14}'
echo ""
echo "===== 3. 模拟 tsensor 发 3 个 NetFlow 明文包到 9996 ====="
(setsid python3 /tmp/udp_dump.py >/tmp/udp_dump.out 2>&1 </dev/null &) >/dev/null 2>&1
sleep 1
python3 - <<'PYEOF'
import socket, struct, time
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# NetFlow v9 头特征: version=9, count, uptime, ts
for i in range(3):
    pkt = struct.pack(">HHII", 9, 1, 1000+i, 2000+i) + bytes([0x11]*16) + f"FLOW-PKT-{i}".encode()
    s.sendto(pkt, ("127.0.0.1", 9996))
    time.sleep(0.3)
print("已发送 3 个包")
PYEOF
sleep 3
echo ""
echo "===== 4. 接收端收到的包（应 3 个完整包） ====="
cat /tmp/udp_dump.out

echo ""
echo "===== 4b. 错误 PSK 客户端（应握手失败） ====="
fuser -k 9997/udp 9998/udp 2>/dev/null; sleep 1
(setsid /root/nftls_build/nftls -m client -l 127.0.0.1:9997 -r 127.0.0.1:19995 -i 设备B -k WRONG_KEY_xxx >/root/nftls_build/cli_bad.log 2>&1 </dev/null &) >/dev/null 2>&1
sleep 3
echo "--- 错误PSK client 日志（应无 tls connected） ---"; grep -c "tls connected" cli_bad.log || echo "0 (握手未成功)"
(setsid /root/nftls_build/nftls -m client -l 127.0.0.1:9998 -r 127.0.0.1:19995 -i 设备B -k key_B_0123456789abcdef >/root/nftls_build/cli_b.log 2>&1 </dev/null &) >/dev/null 2>&1
sleep 2
echo "--- 正确 key 设备B 日志 ---"; grep -c "tls connected" cli_b.log || echo "0"
fuser -k 9997/udp 9998/udp 2>/dev/null; sleep 1
echo ""
echo "===== 5. status 文件（在线状态） ====="
cat test.status 2>/dev/null
echo ""
echo "===== 6. client/server 日志 ====="
echo "--- server ---"; head -3 srv.log
echo "--- client ---"; head -3 cli.log
echo ""
echo "===== 7. tcpdump 抓 19995（验证 TLS 密文） ====="
timeout 3 tcpdump -i lo -c 3 -nn -XX "port 19995" 2>/dev/null | head -25
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