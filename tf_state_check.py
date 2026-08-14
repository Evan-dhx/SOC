import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Check current state", r"""
echo "=== 1. 当前相关进程 ==="
ps aux | grep -E "[e]xtractor|[i]ndexer|[l]aunch_indexer" | grep -v grep | awk '{print $2, $11, $12, $13, $14}' | head -10
echo ""
echo "=== 2. db 现状 ==="
find /Agent/data/db -type f 2>/dev/null | head -10
echo "文件数: $(find /Agent/data/db -type f 2>/dev/null | wc -l)"
echo ""
echo "=== 3. indexer.log 最新 ==="
tail -5 /data/log/indexer.log 2>/dev/null
echo ""
echo "=== 4. flow 最新 ==="
ls -la /Agent/flow/1/ | tail -4
echo ""
echo "=== 5. config 状态 ==="
ls -la /Agent/data/config 2>/dev/null
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
