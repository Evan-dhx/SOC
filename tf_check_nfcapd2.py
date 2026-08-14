import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Check nfcapd status", r"""
echo "=== 1. nfcapd 进程 ==="
ps aux | grep "[n]fcapd"
pidof nfcapd && echo "ALIVE" || echo "DEAD"
echo ""
echo "=== 2. 9995 监听 ==="
ss -tlnup | grep 9995
echo ""
echo "=== 3. nfcapd 日志 ==="
cat /tmp/nfcapd.log 2>/dev/null
echo ""
echo "=== 4. journal 中 nfcapd 相关 ==="
journalctl --no-pager -n 20 2>/dev/null | grep -iE "nfcapd|segfault" | tail -5
echo ""
echo "=== 5. coredump 检查 ==="
ls -lt /var/lib/systemd/coredump/ 2>/dev/null | head -5
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
