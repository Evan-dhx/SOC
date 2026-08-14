import paramiko
import sys
import time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Wait for replay to reach data timestamps
print("[等待 180 秒让 24 小时回放处理到有数据的时间片]")
time.sleep(180)

cmds = [
    ("Check db growth", r"""
echo "=== 1. db 文件（indexer 写入） ==="
find /Agent/data/db -type f 2>/dev/null
echo ""
echo "=== 2. db 文件统计 ==="
find /Agent/data/db -type f 2>/dev/null | wc -l
du -sh /Agent/data/db 2>/dev/null
echo ""
echo "=== 3. eventdb ==="
find /Agent/data/eventdb -type f 2>/dev/null | head -5
du -sh /Agent/data/eventdb 2>/dev/null
echo ""
echo "=== 4. indexer.log 最新 5 行 ==="
tail -5 /data/log/indexer.log 2>/dev/null
echo ""
echo "=== 5. 当前 extractor 处理位置 ==="
ps aux | grep "[e]xtractor" | grep -v bash | head -2 | awk '{print $12, $13, $14, $15}'
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
