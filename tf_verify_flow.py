import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Check flow data files", r"""
echo "=== 1. /data/flow 数据文件 ==="
ls -lh /data/flow/ | tail -10
echo ""
echo "=== 2. 数据文件数量与最新 ==="
ls /data/flow/*.nfcapd* 2>/dev/null | wc -l
ls -lt /data/flow/ | head -5
"""),

    ("Check indexer log from crontab", r"""
echo "=== 3. crontab 执行日志 ==="
ls -lh /data/log/ 2>/dev/null
echo ""
echo "--- indexer.log 尾部 ---"
tail -30 /data/log/indexer.log 2>/dev/null
echo ""
echo "--- config_pusher.log 尾部 ---"
tail -10 /data/log/config_pusher.log 2>/dev/null
"""),

    ("Check extractor needs and launch script", r"""
echo "=== 4. launch_indexer.sh 完整内容 ==="
cat /Agent/bin/launch_indexer.sh
echo ""
echo "=== 5. extractor 依赖 ==="
ldd /Agent/bin/extractor 2>&1 | grep -E "not found|common|protobuf" 
echo ""
echo "=== 6. 手动执行 extractor 测试 ==="
cd /Agent/bin
now=$(date +"%s")
aligned=$[$now-$now%300-300]
echo "aligned=$aligned"
timeout 30 sudo -u apache ./extractor -v 1 -t $aligned -i ./indexer 2>&1 | head -30
echo "Exit: $?"
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
