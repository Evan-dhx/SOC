import paramiko
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('10.10.102.220', username='root', password='PP@ssw0rd', timeout=30)

cmds = [
    ("查找官方 SQL 初始化脚本", r"""
echo "=== 1. ly_server 工程中的 .sql 文件 ==="
find /root/SOC -name "*.sql" -type f 2>/dev/null | grep -v node_modules | head -20
echo ""
echo "=== 2. ly_server_src 目录结构 ==="
ls -la /root/SOC/ly_server_src/
echo ""
echo "=== 3. 部署文档中的建库说明 ==="
grep -rn "CREATE TABLE\|t_mo\|server.sql\|init" /root/SOC/ly_server_src/README.md /root/SOC/ly_server_src/INSTALL.md 2>/dev/null | head -20
echo ""
echo "=== 4. doc 目录 ==="
find /root/SOC/ly_server_src/doc -type f 2>/dev/null | head -10
echo ""
echo "=== 5. 全盘找 server 初始化 sql ==="
find / -name "*.sql" -type f 2>/dev/null | grep -iv "mysql\|wordpress\|test" | head -20
"""),
]

for label, cmd in cmds:
    print(f"\n[{label}]")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=240)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err:
        print(f"STDERR: {err[:2000]}")

client.close()
