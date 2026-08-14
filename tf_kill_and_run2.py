import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Kill with bracket trick", r"""
echo "=== 1. 杀掉并发实例（[x] 技巧防自杀） ==="
pkill -9 -f "[e]xtractor -v" 2>/dev/null
pkill -9 -f "[l]aunch_indexer" 2>/dev/null
pkill -9 -x indexer 2>/dev/null
sleep 2
echo "--- 剩余进程 ---"
ps aux | grep -E "[e]xtractor|[i]ndexer" | grep -v bash | head -5
echo "清理完成"
"""),

    ("Add lock and run once", r"""
echo "=== 2. launch_indexer.sh 加 flock 锁 ==="
cat > /Agent/bin/launch_indexer.sh << 'EOF'
#!/bin/bash

# Prevent concurrent execution
exec 9>/tmp/launch_indexer.lock
if ! flock -n 9; then
  exit 0
fi

cd /Agent/bin

now=`date +"%s"`

aligned_now=$[$now-$now%300-300]

endtime=$[$aligned_now-3600*24]

while [ $endtime -le $aligned_now ]
do
  cmd="sudo -u apache ./extractor -v 1 -t $endtime -i ./indexer"
  $cmd
  endtime=$[$endtime+300]
done
EOF
chmod +x /Agent/bin/launch_indexer.sh
echo "已加锁"
echo ""
echo "=== 3. 手动跑一次（完整回放 288 片） ==="
timeout 900 /Agent/bin/launch_indexer.sh 2>&1 | tail -3
echo "Done, exit: $?"
"""),

    ("Verify db", r"""
echo "=== 4. db 写入结果 ==="
find /Agent/data/db -type f 2>/dev/null | head -20
echo ""
echo "文件数: $(find /Agent/data/db -type f 2>/dev/null | wc -l)"
du -sh /Agent/data/db 2>/dev/null
echo ""
echo "=== 5. eventdb ==="
find /Agent/data/eventdb -type f 2>/dev/null | head -10
du -sh /Agent/data/eventdb 2>/dev/null
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=1200)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()
