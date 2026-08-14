import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("tsensor 传输链路验证", r"""
echo "=== 1. 9995 端口监听情况（UDP/TCP） ==="
ss -ulnp 2>/dev/null | grep 9995
ss -tlnp 2>/dev/null | grep 9995
echo ""
echo "=== 2. 9995 归属进程 ==="
for p in $(ss -ulnp 2>/dev/null | grep 9995 | grep -oP 'pid=\K[0-9]+' | sort -u); do
  ps -p $p -o pid,cmd --no-headers 2>/dev/null
done
echo ""
echo "=== 3. 抓包验证传输内容（10 秒，本机 9995） ==="
timeout 10 tcpdump -i any -c 3 -nn -XX "port 9995" 2>/dev/null | head -40 || echo "tcpdump 抓包完成/无流量"
echo ""
echo "=== 4. tsensor 与采集器关系 ==="
ps aux | grep -E "nfcapd|tsensor" | grep -v grep
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1500]}")

client.close()