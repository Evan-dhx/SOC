import paramiko
import sys
import time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

# Wait for current indexer to finish
print("[等待 60 秒让当前 indexer 完成]")
time.sleep(60)

cmds = [
    ("Check db after indexer run", r"""
echo "=== 1. db 文件 ==="
find /Agent/data/db -type f 2>/dev/null | head -20
echo "文件数: $(find /Agent/data/db -type f 2>/dev/null | wc -l)"
du -sh /Agent/data/db 2>/dev/null
echo ""
echo "=== 2. eventdb ==="
find /Agent/data/eventdb -type f 2>/dev/null | head -10
echo ""
echo "=== 3. flow 完整列表 ==="
ls -la /Agent/flow/1/ | awk '{print $5, $9}'
echo ""
echo "=== 4. indexer.log 最新 ==="
tail -4 /data/log/indexer.log 2>/dev/null
echo ""
echo "=== 5. 进程 ==="
ps aux | grep -E "[e]xtractor|[i]ndexer" | grep -v grep | awk '{print $2, $11, $12, $13}' | head -5
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
