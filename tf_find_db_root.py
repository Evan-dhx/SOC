import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Find AGENT_DB_ROOT definition", r"""
echo "=== AGENT_DB_ROOT / AGENT_EVENT_DB_ROOT 定义 ==="
grep -rn "AGENT_DB_ROOT\|AGENT_EVENT_DB_ROOT" /root/SOC/ly_analyser_src/agent/ 2>/dev/null | grep -v "\.o:" | head -10
echo ""
echo "=== DBBuilder 实现 ==="
grep -rn "class DBBuilder\|DBBuilder::" /root/SOC/ly_analyser_src/agent/data/*.h /root/SOC/ly_analyser_src/agent/data/*.cpp 2>/dev/null | head -10
echo ""
echo "=== unqlite 数据库文件路径 ==="
grep -rn "\.db\|\.udb\|unqlite_open\|unqlite" /root/SOC/ly_analyser_src/agent/data/db_builder* /root/SOC/ly_analyser_src/agent/data/*.h 2>/dev/null | grep -iE "open|\.db|\.udb|path" | head -15
"""),

    ("Check indexer_process marker", r"""
echo "=== indexer_process 文件内容 ==="
cat /Agent/data/indexer_process 2>/dev/null
echo ""
echo "=== 时间对齐（当前） ==="
date +%s
echo ""
echo "=== flow 文件最新 ==="
ls -la /data/flow/ | tail -6
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
