import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("View netflow_v9.c around 1994", r"""
echo "=== netflow_v9.c 1930-2020 ==="
sed -n '1930,2020p' /root/SOC/ly_analyser_src/nfdump/bin/netflow_v9.c
"""),

    ("Find buffer size definitions", r"""
echo "=== 缓冲区大小宏定义 ==="
grep -rn "RECORD_BUF_SIZE\|NETFLOW_MAX\|BUFFER_LEN\|MAX_BUFFER" /root/SOC/ly_analyser_src/nfdump/bin/*.h /root/SOC/ly_analyser_src/nfdump/include/*.h 2>/dev/null | head -20
echo ""
echo "=== nfcapd.c 中缓冲区 ==="
grep -n "bufsize\|buf_size\|buffer\|recvBuffer\|pkt" /root/SOC/ly_analyser_src/nfdump/bin/nfcapd.c 2>/dev/null | head -30
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()
