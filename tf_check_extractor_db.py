import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("View extractor.cpp main flow", r"""
echo "=== extractor.cpp 关键部分 ==="
grep -n "db\|DB\|mysql\|unqlite\|cppdb\|connect\|INSERT\|database" /root/SOC/ly_analyser_src/agent/handlers/extractor.cpp | head -30
echo ""
echo "=== extractor.cpp 处理流程（main） ==="
grep -n -A5 "int main" /root/SOC/ly_analyser_src/agent/handlers/extractor.cpp | head -30
"""),

    ("Check DB config", r"""
echo "=== 数据库配置来源 ==="
grep -rn "ly_agent\|localhost\|3306\|dbname\|database" /root/SOC/ly_analyser_src/agent/handlers/extractor.cpp | head -20
echo ""
echo "=== 配置文件（server 库 t_mo 等） ==="
mysql -e "SELECT * FROM server.t_mo LIMIT 5;" 2>/dev/null | head -10
mysql -e "SHOW TABLES FROM ly_server;" 2>/dev/null | head -20
"""),

    ("Check crontab and indexer log", r"""
echo "=== 当前 crontab ==="
crontab -l 2>/dev/null
echo ""
echo "=== indexer.log 最近 ==="
tail -20 /data/log/indexer.log 2>/dev/null
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
