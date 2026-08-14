import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("extract_feature.cpp 分析", r"""
echo "=== 1. 文件行数 ==="
wc -l /root/SOC/ly_analyser_src/agent/handlers/extract_feature.cpp
echo ""
echo "=== 2. db 路径相关 ==="
grep -n "data/db\|/db\|unqlite\|db_path\|DB_PATH\|AGENT_DATA" /root/SOC/ly_analyser_src/agent/handlers/extract_feature.cpp | head -20
echo ""
echo "=== 3. main/process 结构 ==="
grep -n "int main\|static void\|process\|LoadFromString\|PrintToString\|Query\|FeatureDb" /root/SOC/ly_analyser_src/agent/handlers/extract_feature.cpp | head -25
echo ""
echo "=== 4. type 默认值处理 ==="
grep -n "type\|Type" /root/SOC/ly_analyser_src/agent/handlers/extract_feature.cpp | head -15
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=180)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()
