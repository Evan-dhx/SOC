import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Run extractor+indexer on all slices", r"""
echo "=== 处理所有时间片 ==="
cd /Agent/bin
now=$(date +"%s")
aligned=$[$now-$now%300-300]
echo "aligned=$aligned"
for t in 0 300 600 900 1200 1500 1800 2100 2400; do
  ts=$[$aligned-$t]
  echo "--- extractor -t $ts ---"
  timeout 120 sudo -u apache ./extractor -v 1 -t $ts -i ./indexer 2>&1 | head -8
  echo "Exit: $?"
done
echo "=== 处理完成 ==="
"""),

    ("Check DB data", r"""
echo "=== 数据库事件检查 ==="
mysql -e "SELECT COUNT(*) AS events FROM server.t_event_data;" 2>/dev/null
mysql -e "SELECT COUNT(*) AS agg FROM server.t_event_data_aggre;" 2>/dev/null
echo ""
echo "--- 最近事件（如果有） ---"
mysql -e "SELECT id,time,type,model,devid,level,obj FROM server.t_event_data ORDER BY id DESC LIMIT 8;" 2>/dev/null
echo ""
echo "--- 数据库中的 flow 数据表（agent 库） ---"
mysql -e "SHOW TABLES FROM ly_agent;" 2>/dev/null | head -15
echo ""
echo "--- ly_agent 数据量 ---"
for t in $(mysql -N -e "SHOW TABLES FROM ly_agent;" 2>/dev/null | head -8); do
  cnt=$(mysql -N -e "SELECT COUNT(*) FROM ly_agent.$t;" 2>/dev/null)
  echo "$t: $cnt"
done
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
