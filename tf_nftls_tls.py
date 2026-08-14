import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("TLS record 精确验证", r"""
cd /root/nftls_build
fuser -k 19995/tcp 9996/udp 2>/dev/null; sleep 1
(setsid /root/nftls_build/nftls -m server -l 127.0.0.1:19995 -r 127.0.0.1:19996 -p /root/nftls_build/test.psk -s /root/nftls_build/test.status >srv3.log 2>&1 </dev/null &) >/dev/null 2>&1
sleep 1
(setsid /root/nftls_build/nftls -m client -l 127.0.0.1:9996 -r 127.0.0.1:19995 -i 设备A -k key_A_0123456789abcdef >cli3.log 2>&1 </dev/null &) >/dev/null 2>&1
sleep 2
(setsid timeout 6 tcpdump -i lo -nn -X "port 19995" -c 8 >/tmp/tls_x.txt 2>/dev/null </dev/null &) >/dev/null 2>&1
sleep 1
python3 - <<'PYEOF'
import socket, struct, time
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
for i in range(5):
    pkt = struct.pack(">HHIIII", 9, 1, 100+i, 2000+i, 0x11223344, i) + bytes(range(48))
    s.sendto(pkt, ("127.0.0.1", 9996))
    time.sleep(0.2)
print("已发送 5 个包")
PYEOF
sleep 6
echo "===== 抓包原始 hex（前 2 包，观察 TCP payload 起始字节） ====="
head -30 /tmp/tls_x.txt
echo ""
echo "===== TLS record 判定 ====="
echo -n "ClientHello(16 03 03): "; grep -c "16 03 03" /tmp/tls_x.txt
echo -n "ApplicationData(17 03 03): "; grep -c "17 03 03" /tmp/tls_x.txt
echo -n "明文NetFlow(0009): "; grep -c "0009" /tmp/tls_x.txt || echo 0
fuser -k 19995/tcp 9996/udp 2>/dev/null
echo "已清理"
"""),
]

for label, cmd in cmds:
    print(f"\n{'='*20} {label} {'='*20}")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()