import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Replay with -r option", r"""
echo "=== 回放（正确参数） ==="
echo "--- 回放前 ---"
ls -la /data/flow/
echo ""
echo "--- 回放 ---"
timeout 30 /Agent/bin/nfreplay -H 127.0.0.1 -p 9995 -d 100 -r /data/flow/nfcapd.current 2>&1 | head -10
echo "Replay exit: $?"
echo ""
echo "--- 回放后 ---"
sleep 3
ls -la /data/flow/
stat -c "%s bytes %y" /data/flow/nfcapd.current
"""),

    ("Replay again with all old files", r"""
echo "=== 回放所有历史文件 ==="
for f in /data/flow/nfcapd.*; do
  echo ">>> 回放 $f"
  timeout 30 /Agent/bin/nfreplay -H 127.0.0.1 -p 9995 -d 100 -r $f 2>&1 | head -3
done
echo ""
sleep 3
ls -la /data/flow/
"""),

    ("Process and check DB", r"""
echo "=== 处理并查库 ==="
cd /Agent/bin
now=$(date +"%s")
aligned=$[$now-$now%300-300]
for t in 0 300 600 900; do
  ts=$[$aligned-$t]
  echo "--- extractor -t $ts ---"
  timeout 60 sudo -u apache ./extractor -v 1 -t $ts -i ./indexer 2>&1 | head -5
done
echo ""
echo "=== DB 数据 ==="
mysql -e "SELECT COUNT(*) FROM server.t_event_data;" 2>/dev/null
mysql -e "SELECT COUNT(*) FROM server.t_event_data_aggre;" 2>/dev/null
mysql -e "SELECT id,time,type,model,devid,level FROM server.t_event_data ORDER BY id DESC LIMIT 10;" 2>/dev/null
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=600)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()
