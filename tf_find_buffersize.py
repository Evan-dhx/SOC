import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Find flowset length error logic", r"""
echo "=== 1. flowset length error 源码位置 ==="
grep -rn "flowset length error" /root/SOC/ly_analyser_src/nfdump/ 2>/dev/null | head -5
echo ""
echo "=== 2. Process_v9 函数中的缓冲区检查 ==="
grep -n "buffersize" /root/SOC/ly_analyser_src/nfdump/bin/nfcapd.c 2>/dev/null | head -20
echo ""
echo "=== 3. 缓冲区大小定义 ==="
grep -rn "RECORD_BUF_SIZE\|BUFFER_SIZE\|bufferSize\|BufferSize" /root/SOC/ly_analyser_src/nfdump/bin/nfcapd.c 2>/dev/null | head -20
echo ""
echo "=== 4. flowset length error 上下文 ==="
grep -n -B5 -A10 "flowset length error" /root/SOC/ly_analyser_src/nfdump/bin/nfcapd.c 2>/dev/null | head -40
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
