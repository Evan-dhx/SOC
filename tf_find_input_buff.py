import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Find NETWORK_INPUT_BUFF_SIZE", r"""
echo "=== NETWORK_INPUT_BUFF_SIZE 定义 ==="
grep -rn "NETWORK_INPUT_BUFF_SIZE" /root/SOC/ly_analyser_src/nfdump/bin/nfcapd.c /root/SOC/ly_analyser_src/nfdump/bin/*.h /root/SOC/ly_analyser_src/nfdump/*.h 2>/dev/null | head -10
echo ""
echo "=== nfcapd.c 中 in_buff 分配 ==="
grep -n "in_buff" /root/SOC/ly_analyser_src/nfdump/bin/nfcapd.c | head -10
echo ""
echo "=== netflow_v9.c 的 in_buff 参数 ==="
grep -n "in_buff" /root/SOC/ly_analyser_src/nfdump/bin/netflow_v9.c | head -10
echo ""
echo "=== 所有 BUFF_SIZE 宏 ==="
grep -rn "INPUT_BUFF\|_BUFF_SIZE\|BUFF_LEN" /root/SOC/ly_analyser_src/nfdump/include/*.h /root/SOC/ly_analyser_src/nfdump/bin/*.h 2>/dev/null | head -15
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
