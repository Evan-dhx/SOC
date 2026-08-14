import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Check AGENT_DATA_DIR and db dirs", r"""
echo "=== 1. AGENT_DATA_DIR 定义 ==="
grep -n "AGENT_DATA_DIR\|AGENT_FLOW_DIR" /root/SOC/ly_analyser_src/agent/define.h | head -5
echo ""
echo "=== 2. /Agent/data 结构 ==="
find /Agent/data -type d 2>/dev/null | head -20
echo ""
echo "=== 3. db/eventdb 目录 ==="
ls -la /Agent/data/db/ 2>/dev/null | head -10
ls -la /Agent/data/eventdb/ 2>/dev/null | head -10
echo ""
echo "=== 4. 查找所有 unqlite 数据文件 ==="
find /Agent/data -name "*.db" -o -name "*.udb" 2>/dev/null | head -20
echo ""
echo "=== 5. 最近 5 分钟生成的文件 ==="
find /Agent/data -type f -mmin -5 2>/dev/null | head -20
"""),

    ("Check indexer log progress", r"""
echo "=== 6. indexer.log 最新（crontab 是否在跑） ==="
tail -15 /data/log/indexer.log 2>/dev/null
echo ""
echo "=== 7. 当前 indexer/extractor 进程 ==="
ps aux | grep -E "[i]ndexer|[e]xtractor" | head -5
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
