import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Check flow data accumulation", r"""
echo "=== 1. /data/flow 数据文件（流量是否在积累） ==="
ls -lh /data/flow/
echo ""
echo "=== 2. nfcapd 状态 ==="
ss -tlnup | grep 9995
ps aux | grep "[n]fcapd" | head -2
echo ""
echo "=== 3. 当前 flow 文件大小（与启动时 276B 对比） ==="
stat -c "%s bytes %y" /data/flow/nfcapd.current
"""),

    ("Run full pipeline manually", r"""
echo "=== 4. 手动运行完整处理链路 ==="
cd /Agent/bin
now=$(date +"%s")
aligned=$[$now-$now%300-300]
echo "--- 运行 extractor（当前时间片） ---"
timeout 60 sudo -u apache ./extractor -v 1 -t $aligned -i ./indexer 2>&1 | head -20
echo "Exit: $?"
echo ""
echo "--- 运行 extractor（往前多时间片） ---"
for t in 300 600 900 1200 1500 1800; do
  ts=$[$aligned-$t]
  timeout 60 sudo -u apache ./extractor -v 1 -t $ts -i ./indexer 2>&1 | head -5
done
echo "Done"
"""),

    ("Check DB data", r"""
echo "=== 5. 数据库数据检查 ==="
mysql -e "SHOW DATABASES;" 2>/dev/null | head -20
echo ""
echo "=== 6. 找数据表 ==="
mysql -e "SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema NOT IN ('mysql','information_schema','performance_schema','sys') LIMIT 30;" 2>/dev/null
echo ""
echo "=== 7. 最新数据时间 ==="
mysql -e "SELECT NOW();" 2>/dev/null
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
