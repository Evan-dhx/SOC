import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("View nfcapd.c input buffer", r"""
echo "=== nfcapd.c 400-470（输入缓冲） ==="
sed -n '400,470p' /root/SOC/ly_analyser_src/nfdump/bin/nfcapd.c
echo ""
echo "=== nfcapd.c -B 参数处理 ==="
grep -n -A8 "case 'B'" /root/SOC/ly_analyser_src/nfdump/bin/nfcapd.c | head -15
"""),

    ("View export.c flowBuffer", r"""
echo "=== export.c flowBuffer 定义 ==="
grep -n "flowBuffer" /root/SOC/ly_analyser_src/agent/flow/../flow/../../tsensor/export.c 2>/dev/null | head -5
grep -n "flowBuffer\[" /root/tsensor/export.c | head -5
echo ""
echo "=== export.c 发送部分完整代码 ==="
sed -n '800,880p' /root/tsensor/export.c
echo ""
echo "=== NETFLOW_MAX_BUFFER_LEN 定义 ==="
grep -rn "NETFLOW_MAX_BUFFER_LEN" /root/tsensor/*.h /root/tsensor/*.c 2>/dev/null | head -10
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
