import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Run config_pusher", r"""
echo "=== 1. 运行 config_pusher ==="
cd /Server/bin
timeout 60 ./config_pusher d 2>&1 | head -20
echo "Exit: $?"
echo ""
echo "=== 2. 检查 config 文件 ==="
ls -la /Agent/data/config 2>/dev/null && echo "✅ config 已生成！" || echo "❌ config 未生成"
echo ""
echo "=== 3. config 内容概要 ==="
head -c 500 /Agent/data/config 2>/dev/null | strings | head -10
echo ""
echo "=== 4. config_pusher.log ==="
tail -5 /data/log/config_pusher.log 2>/dev/null
"""),

    ("Trigger extractor", r"""
echo "=== 5. 手动触发 extractor 处理最新时间片 ==="
cd /Agent/bin
now=$(date +"%s")
aligned=$[$now-$now%300-300]
echo "aligned=$aligned"
timeout 120 sudo -u apache ./extractor -v 1 -t $aligned -i ./indexer 2>&1 | head -10
echo "Exit: $?"
echo ""
echo "=== 6. 检查 db 写入 ==="
find /Agent/data/db -type f -mmin -3 2>/dev/null | head -10
echo ""
ls -la /Agent/data/db/20260813/ 2>/dev/null
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=900)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()
