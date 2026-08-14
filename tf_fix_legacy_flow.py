import paramiko
import sys
import time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("处理错位文件 + 验证 db", r"""
echo "=== 1. 错位期文件列表 ==="
ls /Agent/flow/1/nfcapd.2026081313* 2>/dev/null
echo ""
echo "=== 2. 手动处理错位文件（13:09-13:44） ==="
for f in /Agent/flow/1/nfcapd.202608131309 /Agent/flow/1/nfcapd.202608131314 /Agent/flow/1/nfcapd.202608131319 /Agent/flow/1/nfcapd.202608131324 /Agent/flow/1/nfcapd.202608131329 /Agent/flow/1/nfcapd.202608131334 /Agent/flow/1/nfcapd.202608131339 /Agent/flow/1/nfcapd.202608131344; do
  if [ -f "$f" ]; then
    echo ">>> 处理 $f"
    DEVID=1 STARTTIME=1786596300 ENDTIME=1786601400 timeout 120 /Agent/bin/indexer -r "$f" 2>&1 | grep -vE "tensorflow|oneDNN|MLIR" | head -2
  fi
done
echo "处理完成"
echo ""
echo "=== 3. 等待后台 launch_indexer 完成 ==="
for i in $(seq 1 36); do
  if ps aux | grep -q "[l]aunch_indexer.sh" || ps aux | grep -q "[i]ndexer -r"; then
    sleep 10
  else
    echo "已完成（等待 ${i}0 秒）"
    break
  fi
done
echo ""
echo "=== 4. db 文件清单 ==="
find /Agent/data/db -type f 2>/dev/null | sort
echo "文件数: $(find /Agent/data/db -type f 2>/dev/null | wc -l)"
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=900)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()
