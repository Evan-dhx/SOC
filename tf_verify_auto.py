import paramiko
import sys
import time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Wait for crontab cycles and data accumulation
print("[等待 90 秒让 crontab 自动处理 + nfcapd 积累数据]")
time.sleep(90)

cmds = [
    ("Verify automatic pipeline", r"""
echo "=== 1. /Agent/flow/1 数据 ==="
ls -la /Agent/flow/1/ | tail -8
echo ""
echo "=== 2. db 目录（indexer 写入） ==="
find /Agent/data/db -type f 2>/dev/null | head -10
echo ""
echo "=== 3. eventdb ==="
find /Agent/data/eventdb -type f 2>/dev/null | head -10
echo ""
echo "=== 4. indexer.log 最新 10 行 ==="
tail -10 /data/log/indexer.log 2>/dev/null
echo ""
echo "=== 5. config 文件 ==="
ls -la /Agent/data/config /Agent/etc/agent.ini 2>/dev/null
echo ""
echo "=== 6. 运行中的进程 ==="
ps aux | grep -E "[i]ndexer|[e]xtractor|[n]fcapd" | grep -v bash | awk '{print $11, $12, $13, $14}' | head -8
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=300)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()
