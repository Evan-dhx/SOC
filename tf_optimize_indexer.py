import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("优化 launch_indexer 窗口", r"""
echo "=== 1. 当前脚本 ==="
cat /Agent/bin/launch_indexer.sh
echo ""
echo "=== 2. flow 目录旧文件统计 ==="
ls /Agent/flow/1/nfcapd.20260812* 2>/dev/null | wc -l
echo "昨天的文件数（上）; 今天的文件数:"
ls /Agent/flow/1/nfcapd.20260813* 2>/dev/null | wc -l
echo ""
echo "=== 3. 等待当前 indexer 完成（最多 120 秒） ==="
for i in $(seq 1 24); do
  if ps aux | grep -q "[i]ndexer -r"; then
    sleep 5
  else
    echo "indexer 已空闲"
    break
  fi
done
echo ""
echo "=== 4. 删除昨天及更早的 flow 文件（已处理） ==="
rm -f /Agent/flow/1/nfcapd.20260812*
ls /Agent/flow/1/ | head -5
echo ""
echo "=== 5. 修改窗口为 2 小时 ==="
sed -i 's|endtime=$\[$aligned_now-3600\*24\]|endtime=$[$aligned_now-7200]|' /Agent/bin/launch_indexer.sh
grep -n "endtime=\$\[" /Agent/bin/launch_indexer.sh
echo ""
echo "=== 6. 手动跑一次（后台） ==="
nohup /Agent/bin/launch_indexer.sh > /data/log/indexer_manual.log 2>&1 &
echo "已启动，pid $!"
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=600)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()
