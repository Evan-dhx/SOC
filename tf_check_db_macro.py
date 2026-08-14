import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("Check DB macros and my.cnf", r"""
echo "=== 1. define.h 中 DB 宏 ==="
grep -n "SERVER_DB\|DB_CONF" /root/SOC/ly_server_src/server/define.h
echo ""
echo "=== 2. DB_CONF 文件 ==="
grep -n "DB_CONF" /root/SOC/ly_server_src/server/define.h
echo ""
echo "=== 3. my.cnf 配置 ==="
cat /etc/my.cnf 2>/dev/null
ls /etc/my.cnf.d/ 2>/dev/null
cat /etc/my.cnf.d/*.cnf 2>/dev/null | head -30
echo ""
echo "=== 4. 数据库用户检查 ==="
mysql -e "SELECT user, host FROM mysql.user;" 2>/dev/null | head -10
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:1000]}")

client.close()
