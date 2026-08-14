import paramiko
import sys
import time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Check tsensor journal logs", r"""
echo "=== 1. tsensor 完整日志（最近 100 行） ==="
journalctl -u tsensor --no-pager -n 100 2>/dev/null | tail -60
echo ""
echo "=== 2. 当前 tsensor 的文件描述符 ==="
ls -la /proc/$(pidof tsensor)/fd/ 2>/dev/null | head -20
echo ""
echo "=== 3. tsensor 的 socket 状态 ==="
ss -uap | grep tsensor
"""),

    ("Check pcap capture status", r"""
echo "=== 4. tsensor 打开的 pcap/socket ==="
cat /proc/$(pidof tsensor)/net/dev 2>/dev/null | head -5
echo ""
echo "=== 5. ens192 是否 promisc ==="
ip link show ens192 | head -3
echo ""
echo "=== 6. 网卡流量计数（两次采样对比） ==="
cat /proc/net/dev | grep ens192
sleep 5
cat /proc/net/dev | grep ens192
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
