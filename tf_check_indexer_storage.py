import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("View indexer.cpp main", r"""
echo "=== indexer.cpp 关键逻辑 ==="
grep -n "main\|unqlite\|cache\|db\|DB\|open\|write" /root/SOC/ly_analyser_src/agent/indexing/indexer.cpp | head -30
echo ""
echo "=== indexer.cpp main 函数 ==="
grep -n -A30 "int main" /root/SOC/ly_analyser_src/agent/indexing/indexer.cpp | head -50
"""),

    ("View cache_generator", r"""
echo "=== cache_generator.cpp 逻辑 ==="
grep -n "unqlite\|cache\|db\|open\|write\|main" /root/SOC/ly_analyser_src/agent/indexing/cache_generator.cpp | head -30
echo ""
echo "=== flow_indexer.cpp 逻辑 ==="
grep -n "unqlite\|cache\|db\|open\|write\|main" /root/SOC/ly_analyser_src/agent/indexing/flow_indexer.cpp | head -30
"""),

    ("Check unqlite data files", r"""
echo "=== /Agent/data 下数据文件 ==="
find /Agent/data -type f 2>/dev/null | head -20
echo ""
echo "=== unqlite 文件（.db/.udb/.cache） ==="
find /Agent /data /root/SOC -name "*.db" -o -name "*.udb" -o -name "*.cache" -o -name "*.unqlite" 2>/dev/null | grep -v bazel | head -20
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
