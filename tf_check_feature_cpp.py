import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("feature.cpp 函数结构", r"""
echo "=== 1. feature.cpp 全部函数 ==="
grep -n "^[A-Za-z].*(" /root/SOC/ly_server_src/server/feature.cpp | head -30
echo ""
echo "=== 2. 查询 db 文件相关的代码 ==="
grep -n "data/db\|/db/\|unqlite\|op_\|FeatureQuery\|dbpath" /root/SOC/ly_server_src/server/feature.cpp | head -30
echo ""
echo "=== 3. feature.cpp 行数 ==="
wc -l /root/SOC/ly_server_src/server/feature.cpp
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
