import paramiko
import sys
import time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Restart nfcapd with -w", r"""
echo "=== 1. 重启 nfcapd（加 -w 对齐 5 分钟边界） ==="
pkill -x nfcapd 2>/dev/null
sleep 1
/Agent/bin/nfcapd -D -p 9995 -l /Agent/flow/1 -z -b 0.0.0.0 -w
sleep 2
ss -tlnup | grep 9995
ps aux | grep "[n]fcapd" | grep -v grep | awk '{print $2, $11, $12, $13, $14, $15}'
echo ""
echo "=== 2. 手动处理错位期数据（13:46-14:11） ==="
for f in /Agent/flow/1/nfcapd.202608131346 /Agent/flow/1/nfcapd.202608131351 /Agent/flow/1/nfcapd.202608131356 /Agent/flow/1/nfcapd.202608131401 /Agent/flow/1/nfcapd.202608131406 /Agent/flow/1/nfcapd.202608131411; do
  echo ">>> 处理 $f"
  DEVID=1 STARTTIME=1786596300 ENDTIME=1786601400 timeout 120 /Agent/bin/indexer -r "$f" 2>&1 | grep -vE "tensorflow|oneDNN|MLIR" | head -3
done
echo "处理完成"
"""),

    ("Verify db and web", r"""
echo "=== 3. db 文件 ==="
find /Agent/data/db -type f 2>/dev/null | head -20
echo "文件数: $(find /Agent/data/db -type f 2>/dev/null | wc -l)"
du -sh /Agent/data/db 2>/dev/null
echo ""
echo "=== 4. eventdb ==="
find /Agent/data/eventdb -type f 2>/dev/null | head -10
echo ""
echo "=== 5. web feature 接口 ==="
curl -s "http://127.0.0.1/d/feature?action=get&devid=1&starttime=1786596300&endtime=1786601400" 2>&1 | head -c 800
echo ""
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
