import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Loopback replay to test nfcapd", r"""
echo "=== 回放测试（127.0.0.1:9995） ==="
echo "--- 回放前文件状态 ---"
ls -la /data/flow/
echo ""
echo "--- 开始回放 ---"
/Agent/bin/nfreplay -H 127.0.0.1 -p 9995 -d 1000 /data/flow/nfcapd.current 2>&1 | head -10
echo "Replay exit: $?"
echo ""
echo "--- 回放后文件状态 ---"
sleep 2
ls -la /data/flow/
echo ""
stat -c "%s bytes %y" /data/flow/nfcapd.current
"""),

    ("Run extractor on replayed data", r"""
echo "=== 处理回放数据 ==="
cd /Agent/bin
now=$(date +"%s")
aligned=$[$now-$now%300-300]
echo "--- aligned: $aligned ---"
timeout 60 sudo -u apache ./extractor -v 1 -t $aligned -i ./indexer 2>&1 | head -20
echo "Extractor exit: $?"
echo ""
echo "--- 再往前几个时间片 ---"
for t in 300 600; do
  ts=$[$aligned-$t]
  timeout 60 sudo -u apache ./extractor -v 1 -t $ts -i ./indexer 2>&1 | head -10
done
echo "Done"
"""),

    ("Check DB for processed data", r"""
echo "=== 数据库检查 ==="
mysql -e "SELECT COUNT(*) AS event_cnt FROM server.t_event_data;" 2>/dev/null
mysql -e "SELECT COUNT(*) AS agg_cnt FROM server.t_event_data_aggre;" 2>/dev/null
echo ""
echo "--- 最近事件 ---"
mysql -e "SELECT id, event_type, event_time FROM server.t_event_data ORDER BY id DESC LIMIT 5;" 2>/dev/null
echo ""
echo "--- 表结构（确认列名） ---"
mysql -e "DESCRIBE server.t_event_data;" 2>/dev/null | head -15
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
